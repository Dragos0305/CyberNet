System.register(["./index-legacy-Ctu-DfWH.js"],(function(t,e){"use strict";var n,a,l,o,r,c,i,s,u,d,p,g,f,h,_,v,w,x,m,y,T,j,S,C,z,b,k,A;return{setters:[t=>{n=t.d,a=t.r,l=t.o,o=t.c,r=t.w,c=t.u,i=t.B,s=t.b,u=t.e,d=t.I,p=t.f,g=t.C,f=t.y,h=t.D,_=t.h,v=t.i,w=t.x,x=t.j,m=t.q,y=t.s,T=t.F,j=t.t,S=t.v,C=t.k,z=t.p,b=t.z,k=t.A,A=t._}],execute:function(){var e=document.createElement("style");e.textContent="#container[data-v-c529626c]{text-align:center;position:absolute;left:0;right:0;top:50%;transform:translateY(-50%)}#container strong[data-v-c529626c]{font-size:20px;line-height:26px}#container p[data-v-c529626c]{font-size:16px;line-height:22px;color:#8c8c8c;margin:0}#container a[data-v-c529626c]{text-decoration:none}\n",document.head.appendChild(e);const q=t=>(b("data-v-c529626c"),t=t(),k(),t),I=q((()=>v("strong",null,"Train:",-1))),L=q((()=>v("strong",null,"Cargo Type:",-1))),P={class:"traincargo"},R=q((()=>v("strong",null,"Operator:",-1))),$={class:"trainoperator"},B=q((()=>v("p",null,[v("strong",null,"Last seen locations:")],-1)));t("default",A(n({__name:"TrainPage",setup(t){const e=i();let n=a({calltype:"",id:"",cargoType:"",operator:"",lastSeen:[]});return l((()=>{let t=new URLSearchParams({id:e.params.id}).toString(),a=`${window.server}/details?${t}`,l=window.signRequest(a);fetch(a,{headers:{Accept:"application/json","X-Signature":l,"Content-Type":"application/json",Authorization:window.jwt}}).then((t=>t.json())).then((t=>{n.value=t})).catch((t=>{console.log(t)}))})),(t,e)=>(s(),o(c(S),null,{default:r((()=>[u(c(_),{translucent:!0},{default:r((()=>[u(c(d),null,{default:r((()=>[u(c(p),{slot:"start"},{default:r((()=>[u(c(g),{"router-link":"/overview","router-direction":"back"},{default:r((()=>[f("<")])),_:1})])),_:1}),u(c(h),null,{default:r((()=>[f("Train details")])),_:1})])),_:1})])),_:1}),u(c(j),{fullscreen:!0,class:"ion-padding"},{default:r((()=>[v("p",null,[I,f(" "+w(c(n).id),1)]),v("p",null,[L,f(),v("span",P,w(c(n).cargoType),1)]),v("p",null,[R,f(),v("span",$,w(c(n).operator),1)]),B,u(c(x),null,{default:r((()=>[(s(!0),m(T,null,y(c(n).lastSeen,(t=>(s(),o(c(C),null,{default:r((()=>[u(c(z),null,{default:r((()=>[v("h4",null,w(t[0]),1),v("p",null,"lat: "+w(t[1])+" long: "+w(t[2]),1)])),_:2},1024)])),_:2},1024)))),256))])),_:1})])),_:1})])),_:1}))}}),[["__scopeId","data-v-c529626c"]]))}}}));
