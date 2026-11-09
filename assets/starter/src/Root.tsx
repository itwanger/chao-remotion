import React from 'react';
import {Audio, Composition, Sequence, registerRoot, staticFile, useCurrentFrame} from 'remotion';
import film from './film.json';
import {CacheExample} from './CacheExample';
import {C, Popped, Stage} from './components';
import {ChapterShell} from './components/Scenes';
import {FigureRings, type Focus} from './components/FigureFocus';

type Beat = {text:string; label:string; items:string[]; frames:number; audio?:string;
  figure?:{file:string; width:number; height:number; focus:Focus}};
type Chapter = {title:string; beats:Beat[]};
const chapters:Chapter[]=film.chapters as Chapter[];
const length=(chapter:Chapter)=>chapter.beats.reduce((n,b)=>n+b.frames,0);
const ranges=chapters.map((chapter,i)=>{
  const startFrame=chapters.slice(0,i).reduce((n,ch)=>n+length(ch),0);
  return {startFrame,endFrame:startFrame+length(chapter)};
});

// Replace this component for each new mechanism. Objects enter on beat boundaries.
function Scene({beat,step}: {beat:Beat;step:number}) {
  const frame=useCurrentFrame();
  if ('example' in film && film.example==='prefix-cache') return <CacheExample step={step}/>;
  if(beat.figure){
    const fig=beat.figure;
    return <FigureRings file={fig.file} imgW={fig.width} imgH={fig.height} start={0} end={beat.frames}
      rings={[[10,fig.focus,C.blue]]}/>;
  }
  return <div style={{position:'absolute',inset:'180px 120px 205px',display:'flex',flexDirection:'column',justifyContent:'center',gap:66}}>
    <div style={{fontSize:82,fontWeight:650,color:C.ink}}>{beat.label}</div>
    <div style={{display:'flex',alignItems:'center',gap:28}}>
      {beat.items.map((item,i)=><Popped key={i} frame={frame} delay={i*5+2} style={{flex:'1 1 0'}}>
        <div style={{background:i===0?C.blue:C.select,color:i===0?'white':C.ink,borderBottom:'6px solid '+C.blue,
          padding:'38px 16px',fontSize:48,textAlign:'center'}}>{item}</div>
      </Popped>)}
    </div>
  </div>;
}
function Segment({index}:{index:number}){
  const frame=useCurrentFrame();
  const ch=chapters[index];
  let at=0;
  const beats=ch.beats.map(beat=>{const from=at;at+=beat.frames;return {beat,from}});
  const active=beats.find(({from,beat})=>frame>=from&&frame<from+beat.frames);
  return <ChapterShell index={index} chapters={chapters.map(c=>c.title)} brand={film.title} progress={ranges}
    subtitle={active?.beat.text??''}>
    {beats.map(({beat,from},i)=><Sequence key={from} from={from} durationInFrames={beat.frames}>
      <Scene beat={beat} step={index===0?0:i+1}/>{beat.audio&&<Audio src={staticFile(beat.audio)}/>}
    </Sequence>)}
  </ChapterShell>;
}
function Video(){
  return <Stage>{chapters.map((ch,i)=><Sequence key={i} from={ranges[i].startFrame} durationInFrames={length(ch)}>
    <Segment index={i}/>
  </Sequence>)}</Stage>;
}
export const fps=30;
function Root(){
  const size={width:1920,height:1080,fps};
  return <><Composition id="Video" component={Video} {...size} durationInFrames={ranges[ranges.length-1].endFrame}/>
    {chapters.map((ch,i)=><Composition key={i} id={'Chapter'+(i+1)} component={Segment} defaultProps={{index:i}}
      {...size} durationInFrames={length(ch)}/>)}</>;
}
registerRoot(Root);
