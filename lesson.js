/* Each choice loads its own localized movie and native H5P questions. */
(() => {
  const choices=document.querySelector('#language-choice');
  const lesson=document.querySelector('#lesson');
  const container=document.querySelector('#h5p-container');
  const message=document.querySelector('#player-message');
  let selected=null,player=null;
  function update() {
    if (!player?.video) return;
    const settings=window.CASE_ONE_LESSONS[selected];
    const time=player.video.getCurrentTime();
    const caption=settings.captions.find(c=>time>=c[0]&&time<c[1]);
    document.querySelector('#caption').textContent=caption?.[2]||'';
    document.querySelector('#restart').hidden=player.interactions.filter(q=>q.hasFullScore()).length<settings.questions;
  }
  function connect(attempt=0) {
    const frame=container.querySelector('iframe');
    player=[frame?.contentWindow,window].flatMap(c=>c?.H5P?.instances||[])
      .find(p=>typeof p.getVisibleInteractions==='function');
    if (!player?.video) {
      if (attempt<100) return setTimeout(()=>connect(attempt+1),100);
      message.textContent=selected==='english'?'The lesson could not start. Please reload.':'पाठ शुरू नहीं हुआ। कृपया पेज फिर खोलें।';
      return;
    }
    message.hidden=true;
    if (frame) frame.title=selected==='english'?'English electricity and magnetism lesson':'विद्युत और चुंबकत्व का हिंदी पाठ';
    const doc=frame?.contentDocument||document;
    window.LessonQuestionLayout.install(doc,player.$container[0],{
      fallbackTitle:selected==='hinglish'?'सोचकर जवाब दें':'Quick check'
    });
    doc.querySelector('video')?.addEventListener('timeupdate',update);
    player.video.on('stateChange',update);
    player.on('xAPI',()=>setTimeout(update,0));
    document.querySelector('#restart').onclick=()=>{player.resetTask();player.pause();update();};
    window.LessonTools?.install(player,update,selected);
    update();
  }
  async function choose(language) {
    if (selected || !['english','hinglish'].includes(language)) return;
    selected=language;
    const hindi=language==='hinglish';
    document.documentElement.lang=hindi?'hi':'en';
    document.title=hindi?'विद्युत धारा का चुंबकीय प्रभाव · कक्षा 8':'Electricity makes magnetism · Class 8';
    lesson.setAttribute('aria-label',hindi?'प्रयोगशाला का संवादात्मक प्रयोग':'Interactive laboratory experiment');
    choices.hidden=true;lesson.hidden=false;message.hidden=false;
    document.querySelector('#change-language').textContent=hindi?'भाषा बदलें':'Change language';
    document.querySelector('#restart').textContent=hindi?'फिर देखें और कोशिश करें':'Watch and try again';
    document.querySelector('#lesson-title').textContent=hindi?'क्या बिजली से चुंबकीय प्रभाव पैदा हो सकता है?':'Can electricity make a magnet?';
    document.querySelector('#lesson-intro').textContent=hindi?'ताँबे के तार के अंदर देखें। जानें कि विद्युत धारा बहने पर क्या बदलता है।':'Look inside a copper wire. Discover what changes when current flows.';
    document.querySelector('.next-lesson a').textContent=hindi?'अगला प्रयोग: कुंडली और विद्युत चुंबक →':'Next experiment: coils and electromagnets →';
    document.querySelector('.class-label').textContent=hindi?'कक्षा 8 / विज्ञान':'CLASS 8 / SCIENCE';
    document.querySelector('.eyebrow').textContent=hindi?'विद्युत और चुंबकत्व':'ELECTRICITY & MAGNETISM';
    document.querySelector('.brand').textContent=hindi?'प्रयोगशाला':'FIELD NOTES';
    document.querySelector('.skip-link').textContent=hindi?'पाठ पर जाएँ':'Skip to lesson';
    message.textContent=hindi?'आपका पाठ खुल रहा है…':'Loading your lesson…';
    document.querySelector('#change-language').focus();
    try {
      const settings=window.CASE_ONE_LESSONS[language];
      const total=Math.round(settings.duration);
      document.querySelector('#lesson-length').textContent=`${Math.floor(total/60)}:${String(total%60).padStart(2,'0')}`;
      await new window.H5PStandalone.H5P(container,{
        id:`case-one-${language}`,h5pJsonPath:settings.path,
        frameJs:'vendor/h5p-player/frame.bundle.js',frameCss:'vendor/h5p-player/styles/h5p.css',
        customCss:'h5p-theme.css',frame:true,icon:true,fullScreen:true,
        export:false,embed:false,copyright:false,reportingIsEnabled:false,
        postUserStatistics:false,saveFreq:false
      });
      connect();
    } catch {
      message.textContent=hindi?'पाठ नहीं खुला। भाषा बदलकर फिर कोशिश करें।':'The lesson could not load. Use Change language to try again.';
    }
  }
  choices.querySelectorAll('[data-language]').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.language)));
  document.querySelector('#change-language').addEventListener('click',()=>{player?.pause();window.location.reload();});
})();
