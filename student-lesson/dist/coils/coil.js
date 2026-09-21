/* Language selection loads exactly one genuine H5P Interactive Video. */
(() => {
  const choices=document.querySelector('#language-choice');
  const lesson=document.querySelector('#lesson');
  const container=document.querySelector('#h5p-container');
  const message=document.querySelector('#player-message');
  let selected=null,player=null;
  function update() {
    if (!player?.video) return;
    const settings=window.COIL_LESSONS[selected];
    const time=player.video.getCurrentTime();
    const caption=settings.captions.find(c=>time>=c[0]&&time<c[1]);
    document.querySelector('#caption').textContent=caption?.[2]||'';
    const answered=player.interactions.filter(q=>q.hasFullScore()).length;
    document.querySelector('#progress').textContent=selected==='english'
      ? `English · ${answered} of ${settings.questions} questions completed`
      : `Hinglish · ${settings.questions} में से ${answered} सवाल पूरे`;
    document.querySelector('#replay').hidden=answered<settings.questions;
  }
  function connect(attempt=0) {
    const frame=container.querySelector('iframe');
    player=[frame?.contentWindow,window].flatMap(c=>c?.H5P?.instances||[])
      .find(p=>typeof p.getVisibleInteractions==='function');
    if (!player?.video) {
      if (attempt<100) return setTimeout(()=>connect(attempt+1),100);
      message.textContent='The lesson could not start. Please reload and try again.';
      return;
    }
    message.hidden=true;
    if (frame) frame.title=`${selected==='english'?'English':'Hinglish'} electromagnet lesson and questions`;
    const doc=frame?.contentDocument||document;
    window.LessonQuestionLayout.install(doc,player.$container[0]);
    doc.querySelector('video')?.addEventListener('timeupdate',update);
    player.video.on('stateChange',update);
    player.on('xAPI',()=>setTimeout(update,0));
    document.querySelector('#replay').onclick=()=>{player.resetTask();player.pause();update();};
    update();
  }
  async function choose(language) {
    if (selected || !['english','hinglish'].includes(language)) return;
    selected=language;
    document.documentElement.lang=language==='english'?'en':'hi';
    choices.hidden=true;lesson.hidden=false;
    message.hidden=false;
    document.querySelector('#change-language').focus();
    try {
      const settings=window.COIL_LESSONS[language];
      await new window.H5PStandalone.H5P(container,{
        id:`coil-${language}`,h5pJsonPath:settings.path,
        frameJs:'../vendor/h5p-player/frame.bundle.js',frameCss:'../vendor/h5p-player/styles/h5p.css',
        customCss:'../h5p-theme.css',frame:true,icon:true,fullScreen:true,
        export:false,embed:false,copyright:false,reportingIsEnabled:false,
        postUserStatistics:false,saveFreq:false
      });
      connect();
    } catch {
      message.textContent='The lesson could not load. Use Change language to restart.';
    }
  }
  choices.querySelectorAll('[data-language]').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.language)));
  document.querySelector('#change-language').addEventListener('click',()=>{
    player?.pause();window.location.reload();
  });
})();
