const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require('jsdom');

const root = path.resolve(__dirname, '..');
const language=process.env.COIL_LANGUAGE;
if (language && !['english','hinglish'].includes(language)) throw new Error('Invalid coil language');
const packageDir = path.join(root, language ? `dist/h5p/coil-${language}` : 'dist/h5p/electromagnetism');
let narrationPath=language ? path.join(root,`../output/parts/02_coil_reversal/bilingual/audio_${language}/narration-timing.json`) : path.join(root,'content/narration-timing.json');
if (language && !fs.existsSync(narrationPath)) {
  narrationPath=path.join(root,`../archive/generated/parts/02_coil_reversal/bilingual/audio_${language}/narration-timing.json`);
}
const checkLabel=language==='hinglish'?'जवाब जाँचें':'Check answer';
const retryLabel=language==='hinglish'?'फिर कोशिश करें':'Try again';
const continueLabel=language==='hinglish'?'आगे बढ़ें':'Continue video';
const read = filename => JSON.parse(fs.readFileSync(filename, 'utf8'));
const manifest = read(path.join(packageDir, 'h5p.json'));
const params = read(path.join(packageDir, 'content/content.json'));
const questions = read(path.join(root, language ? `content/coil/${language}.json` : 'content/questions.json'));
const duration = read(narrationPath).duration;

function nativeH5P() {
  const errors = [];
  const console = new VirtualConsole();
  console.on('jsdomError', error => errors.push(error.message));
  console.on('error', (...messages) => process.stderr.write(messages.join(' ') + '\n'));
  const dom = new JSDOM('<!doctype html><div id="player"></div>', {
    url: 'https://lesson.test/', runScripts: 'outside-only', pretendToBeVisual: true,
    virtualConsole: console,
  });
  const w = dom.window;
  w.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {} });
  // This unit test exercises native scoring, without a browser layout engine.
  w.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
  w.H5PIntegration = { baseUrl: 'https://lesson.test', url: '/h5p',
    libraryUrl: '/vendor/h5p-player', l10n: { H5P: {} }, saveFreq: false,
    postUserStatistics: false, contents: { 'cid-1': {
      library: 'H5P.InteractiveVideo 1.28', jsonContent: JSON.stringify(params),
      url: 'https://lesson.test/', metadata: { title: 'Electromagnetism', license: 'U' },
    } }, core: { scripts: [], styles: [] } };
  w.eval(fs.readFileSync(path.join(root, 'dist/vendor/h5p-player/frame.bundle.js'), 'utf8'));
  w.H5P.preventInit = true;
  const loaded = new Set();
  function load(dependency) {
    const name = `${dependency.machineName}-${dependency.majorVersion}.${dependency.minorVersion}`;
    if (loaded.has(name)) return;
    const library = read(path.join(packageDir, name, 'library.json'));
    for (const dep of library.preloadedDependencies || []) load(dep);
    for (const source of library.preloadedJs || []) {
      w.eval(fs.readFileSync(path.join(packageDir, name, source.path), 'utf8'));
    }
    loaded.add(name);
  }
  manifest.preloadedDependencies.forEach(load);
  w.eval(fs.readFileSync(path.join(root, 'dist/question-layout.js'), 'utf8'));
  w.LessonQuestionLayout.install(w.document, w.document.querySelector('#player'));
  return { dom, w, errors };
}

test('genuine H5P library closure and content assets are complete', () => {
  assert.equal(manifest.mainLibrary, 'H5P.InteractiveVideo');
  for (const dependency of manifest.preloadedDependencies) {
    const name = `${dependency.machineName}-${dependency.majorVersion}.${dependency.minorVersion}`;
    const meta = read(path.join(packageDir, name, 'library.json'));
    for (const asset of [...(meta.preloadedJs || []), ...(meta.preloadedCss || [])]) {
      assert.ok(fs.statSync(path.join(packageDir, name, asset.path)).size > 0, `${name}/${asset.path}`);
    }
    for (const dep of meta.preloadedDependencies || []) {
      assert.ok(manifest.preloadedDependencies.some(item => JSON.stringify(item) === JSON.stringify(dep)), `${name} has a missing dependency`);
    }
  }
  const video = params.interactiveVideo.video;
  assert.ok(fs.statSync(path.join(packageDir, 'content', video.files[0].path)).size > 1_000_000);
  assert.ok(fs.existsSync(path.join(packageDir, 'content', video.startScreenOptions.poster.path)));
  assert.equal(params.override.autoplay, false);
  assert.equal(params.override.hasNoAutoPause, false);
  assert.deepEqual(params.interactiveVideo.assets.endscreens, [], 'The final laboratory summary stays visible');
  if (fs.existsSync(narrationPath)) {
    const timing = read(narrationPath);
    assert.equal(params.override.deactivateSound, false, 'Narrated lessons must enable audio');
    assert.equal(duration, timing.duration);
    params.interactiveVideo.assets.interactions.forEach((interaction, index) => {
      const section = language ? timing.segments.find(s=>s.id===questions[index].after_id) : timing.segments[questions[index].after_section - 1];
      const speechStart = section.speech_start ?? Math.round((section.target_start + .2) * timing.fps) / timing.fps;
      const speechEnd = speechStart + section.speech_seconds;
      assert.ok(interaction.duration.from > speechEnd + .1, 'Questions follow the complete explanation');
    });
  }
  assert.equal(questions.length, language ? 4 : 2);
  assert.equal(params.interactiveVideo.assets.interactions.length, questions.length);
  for (const interaction of params.interactiveVideo.assets.interactions) {
    assert.equal(interaction.action.library, 'H5P.MultiChoice 1.16');
    assert.equal(interaction.pause, true);
    assert.equal(interaction.adaptivity.requireCompletion, true);
    assert.equal(interaction.displayType, 'button');
    assert.ok(interaction.duration.from < duration);
  }
});

test('upstream H5P questions score wrong answers, retry, and score correct answers', async () => {
  const { dom, w, errors } = nativeH5P();
  try {
    const parent = w.H5P.newRunnable(w.JSON.parse(JSON.stringify({
      library: 'H5P.InteractiveVideo 1.28', params,
    })), 1);
    parent.video = { getCurrentTime: () => 8.5, getDuration: () => duration };
    assert.equal(parent.interactions.length, questions.length);
    const wrapper = w.document.createElement('div');
    wrapper.className = 'h5p-dialog';
    wrapper.dataset.lib = 'H5P.MultiChoice';
    wrapper.innerHTML = '<div class="h5p-dialog-title"></div><div class="h5p-dialog-inner" id="question"></div>';
    w.document.querySelector('#player').replaceChildren(wrapper);
    const host = w.H5P.jQuery(wrapper);
    for (const [index, interaction] of parent.interactions.entries()) {
      const question = interaction.getInstance();
      // InteractiveVideo reuses its dialog, replacing only the inner content.
      question.attach(host.find('#question').empty());
      await new Promise(resolve => setTimeout(resolve, 0));
      assert.ok(wrapper.querySelector('.lesson-question-actions button'), 'Check stays in the fixed footer');
      assert.equal(wrapper.querySelectorAll('.lesson-question-actions .h5p-question-buttons').length, 1,
        'Only the current question keeps its controls');
      assert.equal(wrapper.querySelector('.lesson-question-actions').textContent.trim(), checkLabel,
        'Earlier Continue buttons are removed when the next question opens');
      assert.equal(question.getMaxScore(), 1);
      let radios = host.find('[role="radio"]');
      assert.equal(radios.length, 3);
      radios.get((questions[index].correct + 1) % 3).click();
      host.find('button').filter((_, el) => el.textContent.trim() === checkLabel).get(0).click();
      assert.equal(question.getScore(), 0, `question ${index + 1} wrong answer`);
      assert.ok(host.text().includes(questions[index].hint));
      assert.ok(question.hasButton('try-again'));
      await new Promise(resolve => setTimeout(resolve, 300));
      host.find('button').filter((_, el) => el.textContent.trim() === retryLabel).get(0).click();
      await new Promise(resolve => setTimeout(resolve, 300));
      radios = host.find('[role="radio"]');
      radios.get(questions[index].correct).click();
      const checkAgain = host.find('button').filter((_, el) => el.textContent.trim() === checkLabel).get(0);
      assert.ok(checkAgain, host.find('button').map((_, el) => el.outerHTML).get().join('\n'));
      checkAgain.click();
      assert.equal(question.getScore(), 1, `question ${index + 1} correct answer`);
      assert.ok(host.text().includes(questions[index].success));
      assert.equal(interaction.hasFullScore(), true);
      assert.ok(question.hasButton('iv-continue'), 'H5P provides native continue');
      await new Promise(resolve => setTimeout(resolve, 0));
      assert.equal(wrapper.querySelector('.lesson-question-actions button').textContent.trim(), continueLabel);
    }
    assert.deepEqual(errors, []);
  } finally { dom.window.close(); }
});
