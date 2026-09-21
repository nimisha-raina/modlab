const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
for(const language of ['english','hinglish']) {
  test(`Case 1 loads only the selected ${language} movie and questions`,()=>{
    const dom=new JSDOM(fs.readFileSync(path.join(root,'dist/index.html'),'utf8'),{
      url:'https://lesson.test/',runScripts:'outside-only'});
    try {
      const w=dom.window,calls=[];
      w.CASE_ONE_LESSONS={english:{path:'./h5p/case-one-english',duration:146.75},hinglish:{path:'./h5p/case-one-hinglish',duration:176.583}};
      w.H5PStandalone={H5P:function(container,options){calls.push(options);return new Promise(()=>{});}};
      w.eval(fs.readFileSync(path.join(root,'dist/lesson.js'),'utf8'));
      assert.equal(calls.length,0);
      assert.equal(w.document.querySelector('#lesson').hidden,true);
      w.document.querySelector(`[data-language="${language}"]`).click();
      assert.equal(calls.length,1);
      assert.equal(calls[0].h5pJsonPath,`./h5p/case-one-${language}`);
      assert.equal(w.document.querySelector('#language-choice').hidden,true);
      assert.equal(w.document.querySelector('#lesson').hidden,false);
      assert.equal(w.document.documentElement.lang,language==='english'?'en':'hi');
      assert.equal(w.document.title,language==='english'?'Electricity makes magnetism · Class 8':'विद्युत धारा का चुंबकीय प्रभाव · कक्षा 8');
      w.document.querySelector('[data-language="english"]').click();
      assert.equal(calls.length,1,'A repeated click cannot start simultaneous soundtracks');
      assert.equal(calls[0].postUserStatistics,false);
      assert.equal(w.document.querySelector('#progress-text'),null);
      assert.equal(w.document.querySelector('.video-note'),null);
      assert.equal(w.document.querySelector('.lesson-footer'),null);
    } finally {dom.window.close();}
  });
}
