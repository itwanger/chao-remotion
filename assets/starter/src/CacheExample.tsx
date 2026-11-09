import React from 'react';
import {interpolate,useCurrentFrame} from 'remotion';
import {C,MONO} from './components';

/** The same four cache cells stay registered across all three narration beats. */
export function CacheExample({step}:{step:number}){
  const f=useCurrentFrame();
  const progress=(a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  const append=step===2;
  return <div style={{position:'absolute',inset:'195px 146px 210px'}}>
    <div style={{fontSize:68,fontWeight:650,marginBottom:62}}>{['第一次请求','复用相同前缀','只计算新增部分'][step]}</div>
    <div style={{display:'flex',gap:22}}>
      {['系统','角色','工具','定义',...(append?['新问题']:[])].map((text,i)=>{
        const t=step===0?progress(i*7,i*7+9):i===4?progress(2,14):1;
        const hit=step===1?progress(i*7,i*7+7):0;
        return <div key={text} style={{width:253,opacity:t,transform:'translateY('+((1-t)*24)+'px)'}}>
          <div style={{height:120,display:'grid',placeItems:'center',background:i===4?C.rust:C.blue,color:'white',fontSize:46}}>{text}</div>
          <div style={{marginTop:36,height:7,width:(step===0?progress(i*7+9,i*7+24):1)*100+'%',background:i===4?C.rust:C.soft}}/>
          <div style={{marginTop:15,padding:'23px 0',textAlign:'center',background:hit>.5?C.select:C.card,color:i===4?C.rust:C.blue,
            fontFamily:MONO,fontSize:38,opacity:step===0?progress(i*7+12,i*7+23):i===4?progress(14,24):1}}>
            K{i+1} · V{i+1}
          </div>
        </div>;
      })}
    </div>
  </div>;
}
