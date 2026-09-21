const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {JSDOM}=require('jsdom');
const root=path.resolve(__dirname,'..');
for(const language of ['english','hinglish']) {
  test(`language choice loads only the selected ${language} lesson`,()=>{
    const dom=new JSDOM(fs.readFileSync(path.join(root,'dist/coils/index.html'),'utf8'),{
      url:'https://lesson.test/coils/',runScripts:'outside-only'});
    try {
      const w=dom.window,calls=[];
      w.COIL_LESSONS={english:{path:'../h5p/coil-english'},hinglish:{path:'../h5p/coil-hinglish'}};
      w.H5PStandalone={H5P:function(container,options){calls.push(options);return new Promise(()=>{});}};
      w.eval(fs.readFileSync(path.join(root,'dist/coils/coil.js'),'utf8'));
      assert.equal(calls.length,0,'No narration or player loads before a choice');
      assert.equal(w.document.querySelector('#lesson').hidden,true);
      w.document.querySelector(`[data-language="${language}"]`).click();
      assert.equal(calls.length,1);
      assert.equal(calls[0].h5pJsonPath,`../h5p/coil-${language}`);
      assert.equal(w.document.querySelector('#language-choice').hidden,true);
      assert.equal(w.document.querySelector('#lesson').hidden,false);
      assert.equal(w.document.documentElement.lang,language==='english'?'en':'hi');
      w.document.querySelector('[data-language="english"]').click();
      assert.equal(calls.length,1,'Repeated clicks do not create a second player or soundtrack');
      assert.equal(calls[0].postUserStatistics,false);
    } finally {dom.window.close();}
  });
}
