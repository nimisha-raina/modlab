/* H5P owns the video, questions, scoring, feedback, and continuation controls.
   This small adapter supplies the surrounding captions and replay button. */
(() => {
  const container = document.querySelector('#h5p-container');
  const message = document.querySelector('#player-message');
  const progress = document.querySelector('#progress-text');
  const restart = document.querySelector('#restart');
  let player;
  let captionIndex = -1;
  const metadata = window.LESSON_METADATA;
  if (metadata) document.querySelector('.lesson-length').textContent = `${Math.round(metadata.duration)}-second video · Go at your own pace`;
  if (metadata) document.querySelector('.video-note').textContent = metadata.narrated
    ? 'Indian-English narration · English captions · Video and voice pause together for each question.'
    : 'English captions · The video pauses for each question.';

  function update() {
    if (!player?.video) return;
    const time = player.video.getCurrentTime();
    const index = window.LESSON_CAPTIONS.findIndex(c => time >= c[0] && time < c[1]);
    if (index >= 0 && index !== captionIndex) {
      captionIndex = index;
      document.querySelector('#caption-title').textContent = window.LESSON_CAPTIONS[index][2];
      document.querySelector('#caption-detail').textContent = window.LESSON_CAPTIONS[index][3];
    }
    const answered = player.interactions.filter(item => item.hasFullScore()).length;
    const total = metadata?.questions ?? player.interactions.length;
    progress.textContent = answered ? `${answered} of ${total} explored` : `${total} questions inside the video`;
    restart.hidden = answered < total;
  }

  function nativePlayer() {
    const frame = container.querySelector('iframe');
    const contexts = [frame?.contentWindow, window];
    for (const context of contexts) {
      const found = context?.H5P?.instances?.find(item => typeof item.getVisibleInteractions === 'function');
      if (found) return found;
    }
  }

  function connect(attempt = 0) {
    player = nativePlayer();
    if (!player?.video) {
      if (attempt < 100) return setTimeout(() => connect(attempt + 1), 100);
      message.textContent = 'The lesson could not start. Refresh the page to try again.';
      return;
    }
    message.hidden = true;
    const frame = container.querySelector('iframe');
    if (frame) frame.title = 'Interactive electromagnetism video and questions';
    window.LessonQuestionLayout.install(frame?.contentDocument || document, player.$container[0]);
    const video = frame?.contentDocument?.querySelector('video') || container.querySelector('video');
    video?.addEventListener('timeupdate', update);
    player.video.on('stateChange', update);
    player.on('xAPI', () => setTimeout(update, 0));
    restart.addEventListener('click', () => { player.resetTask(); player.pause(); update(); });
    registerAgentTools();
    update();
  }

  function visibleQuestion() {
    return player?.getVisibleInteractions().find(item => item.getElement()?.[0]?.isConnected);
  }

  // Keep the optional agent controls connected to the native H5P answer form.
  function registerAgentTools() {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const register = tool => {
      try { Promise.resolve(context.registerTool(tool, { signal: lifecycle.signal })).catch(() => {}); } catch {}
    };
    const radios = () => [...player.$container[0].querySelectorAll('.h5p-dialog [role="radio"]')];
    register({ name: 'get_lesson_progress', description: 'Read the genuine H5P video progress and visible question.',
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
      annotations: { readOnlyHint: true, untrustedContentHint: false },
      execute: () => ({ seconds: player.video.getCurrentTime(),
        completed: player.interactions.map((item, i) => item.hasFullScore() ? i + 1 : null).filter(Boolean),
        currentQuestion: visibleQuestion() ? { title: visibleQuestion().getTitle(),
          options: radios().map(el => el.textContent.trim()) } : null }) });
    register({ name: 'answer_current_question', description: 'Select and check an answer through the visible native H5P question controls.',
      inputSchema: { type: 'object', properties: { choice: { type: 'integer', minimum: 0, maximum: 2 } }, required: ['choice'], additionalProperties: false },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      execute: input => {
        if (!input || typeof input !== 'object' || Object.keys(input).some(key => key !== 'choice') || !Number.isInteger(input.choice) || input.choice < 0 || input.choice > 2) throw new Error('Provide one answer index between zero and two.');
        const item = visibleQuestion();
        const options = radios();
        const check = [...player.$container[0].querySelectorAll('.h5p-dialog button')].find(button => button.textContent.trim() === 'Check answer');
        if (!item || !options[input.choice] || options[input.choice].getAttribute('aria-disabled') === 'true' || !check) throw new Error('No unanswered H5P question is currently open.');
        options[input.choice].click();
        check.click();
        update();
        return { correct: item.hasFullScore(), feedback: player.$container[0].querySelector('.h5p-dialog .h5p-question-feedback')?.textContent.trim() || '' };
      } });
    window.addEventListener('pagehide', () => lifecycle.abort(), { once: true });
  }

  try {
    new window.H5PStandalone.H5P(container, {
      id: 'electromagnetism-class8',
      h5pJsonPath: './h5p/electromagnetism',
      frameJs: './vendor/h5p-player/frame.bundle.js',
      frameCss: './vendor/h5p-player/styles/h5p.css',
      customCss: './h5p-theme.css',
      frame: true, icon: true, fullScreen: true,
      export: false, embed: false, copyright: false,
      reportingIsEnabled: false, postUserStatistics: false, saveFreq: false,
    }).then(() => connect()).catch(() => {
      message.textContent = 'The lesson could not load. Check your connection, then refresh the page.';
    });
  } catch {
    message.textContent = 'The lesson could not load. Check your connection, then refresh the page.';
  }
})();
