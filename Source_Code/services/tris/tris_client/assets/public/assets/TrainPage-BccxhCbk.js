import{d as h,r as I,o as w,c as f,w as a,u as e,B as m,b as p,e as n,I as T,f as S,C as v,y as c,D as y,h as B,i as t,x as o,j as k,q as x,s as C,F as j,t as L,v as P,k as b,p as V,z as A,A as D,_ as N}from"./index-C6DMi5pG.js";const u=i=>(A("data-v-c529626c"),i=i(),D(),i),R=u(()=>t("strong",null,"Train:",-1)),q=u(()=>t("strong",null,"Cargo Type:",-1)),z={class:"traincargo"},E=u(()=>t("strong",null,"Operator:",-1)),F={class:"trainoperator"},U=u(()=>t("p",null,[t("strong",null,"Last seen locations:")],-1)),$=h({__name:"TrainPage",setup(i){const g=m();let s=I({calltype:"",id:"",cargoType:"",operator:"",lastSeen:[]});return w(()=>{let _=new URLSearchParams({id:g.params.id}).toString(),d="".concat(window.server,"/details?").concat(_),l=window.signRequest(d);fetch(d,{headers:{Accept:"application/json","X-Signature":l,"Content-Type":"application/json",Authorization:window.jwt}}).then(r=>r.json()).then(r=>{s.value=r}).catch(r=>{console.log(r)})}),(_,d)=>(p(),f(e(P),null,{default:a(()=>[n(e(B),{translucent:!0},{default:a(()=>[n(e(T),null,{default:a(()=>[n(e(S),{slot:"start"},{default:a(()=>[n(e(v),{"router-link":"/overview","router-direction":"back"},{default:a(()=>[c("<")]),_:1})]),_:1}),n(e(y),null,{default:a(()=>[c("Train details")]),_:1})]),_:1})]),_:1}),n(e(L),{fullscreen:!0,class:"ion-padding"},{default:a(()=>[t("p",null,[R,c(" "+o(e(s).id),1)]),t("p",null,[q,c(),t("span",z,o(e(s).cargoType),1)]),t("p",null,[E,c(),t("span",F,o(e(s).operator),1)]),U,n(e(k),null,{default:a(()=>[(p(!0),x(j,null,C(e(s).lastSeen,l=>(p(),f(e(b),null,{default:a(()=>[n(e(V),null,{default:a(()=>[t("h4",null,o(l[0]),1),t("p",null,"lat: "+o(l[1])+" long: "+o(l[2]),1)]),_:2},1024)]),_:2},1024))),256))]),_:1})]),_:1})]),_:1}))}}),O=N($,[["__scopeId","data-v-c529626c"]]);export{O as default};