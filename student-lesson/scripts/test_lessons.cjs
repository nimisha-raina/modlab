/* Run the frozen reference and both languages of both current lessons. */
const path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const environment={...process.env};
delete environment.CASE_ONE_LANGUAGE;
delete environment.COIL_LANGUAGE;
function run(files,extra={}) {
  const result=spawnSync(process.execPath,['--test',...files],{
    cwd:root,env:{...environment,...extra},stdio:'inherit'
  });
  if(result.error) throw result.error;
  if(result.status!==0) process.exit(result.status??1);
}
run(['tests/h5p.test.cjs','tests/case-one-language.test.cjs','tests/coil-language.test.cjs']);
for(const key of ['CASE_ONE_LANGUAGE','COIL_LANGUAGE']) {
  for(const language of ['english','hinglish']) run(['tests/h5p.test.cjs'],{[key]:language});
}
