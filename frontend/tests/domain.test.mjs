import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
const source=readFileSync(new URL('../src/domain.ts',import.meta.url),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {dollarsToCents,validateFacts,defaultCar,sortCars}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
test('dollars convert exactly to integer cents at the API boundary',()=>{
 for(const [dollars,cents] of [['23500',2350000],['23500.01',2350001],['0.29',29],['0',0],['1.1',110]])assert.equal(dollarsToCents(dollars),cents);
 for(const invalid of ['','-1','1.001','NaN','Infinity','1e3','10000001'])assert.throws(()=>dollarsToCents(invalid));
});
test('invalid facts fail with friendly messages',()=>{
 const good={make:'Toyota',model:'Camry',year:2022,price:2350000,mileage:42000,availability:'available'};
 validateFacts(good);
 for(const [key,value] of [['make',' '],['model',''],['year',2200],['price',-1],['mileage',-1],['mileage',1.5]])assert.throws(()=>validateFacts({...good,[key]:value}));
});
test('latest published Camry is preferred over duplicates and drafts',()=>{
 const facts={make:'Toyota',model:'Camry',year:2022};
 const cars=[{id:'draft',facts,published_revision:null},{id:'old',facts,published_revision:3,published_at:'2026-11-04'},{id:'latest',facts,published_revision:7,published_at:'2026-11-05'}];
 assert.equal(defaultCar(cars).id,'latest');assert.deepEqual(sortCars(cars).map(c=>c.id),['latest','old','draft']);
});
