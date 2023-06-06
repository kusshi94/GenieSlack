"use strict";(self.webpackChunkgatsby_starter_default=self.webpackChunkgatsby_starter_default||[]).push([[351],{3204:function(e){const t=/[\p{Lu}]/u,a=/[\p{Ll}]/u,r=/^[\p{Lu}](?![\p{Lu}])/gu,n=/([\p{Alpha}\p{N}_]|$)/u,i=/[_.\- ]+/,s=new RegExp("^"+i.source),o=new RegExp(i.source+n.source,"gu"),c=new RegExp("\\d+"+n.source,"gu"),l=(e,n)=>{if("string"!=typeof e&&!Array.isArray(e))throw new TypeError("Expected the input to be `string | string[]`");if(n={pascalCase:!1,preserveConsecutiveUppercase:!1,...n},0===(e=Array.isArray(e)?e.map((e=>e.trim())).filter((e=>e.length)).join("-"):e.trim()).length)return"";const i=!1===n.locale?e=>e.toLowerCase():e=>e.toLocaleLowerCase(n.locale),l=!1===n.locale?e=>e.toUpperCase():e=>e.toLocaleUpperCase(n.locale);if(1===e.length)return n.pascalCase?l(e):i(e);return e!==i(e)&&(e=((e,r,n)=>{let i=!1,s=!1,o=!1;for(let c=0;c<e.length;c++){const l=e[c];i&&t.test(l)?(e=e.slice(0,c)+"-"+e.slice(c),i=!1,o=s,s=!0,c++):s&&o&&a.test(l)?(e=e.slice(0,c-1)+"-"+e.slice(c-1),o=s,s=!1,i=!0):(i=r(l)===l&&n(l)!==l,o=s,s=n(l)===l&&r(l)!==l)}return e})(e,i,l)),e=e.replace(s,""),e=n.preserveConsecutiveUppercase?((e,t)=>(r.lastIndex=0,e.replace(r,(e=>t(e)))))(e,i):i(e),n.pascalCase&&(e=l(e.charAt(0))+e.slice(1)),((e,t)=>(o.lastIndex=0,c.lastIndex=0,e.replace(o,((e,a)=>t(a))).replace(c,(e=>t(e)))))(e,l)};e.exports=l,e.exports.default=l},8032:function(e,t,a){a.d(t,{L:function(){return m},M:function(){return _},P:function(){return E},S:function(){return D},_:function(){return o},a:function(){return s},b:function(){return d},g:function(){return u},h:function(){return c}});var r=a(7294),n=(a(3204),a(5697)),i=a.n(n);function s(){return s=Object.assign?Object.assign.bind():function(e){for(var t=1;t<arguments.length;t++){var a=arguments[t];for(var r in a)Object.prototype.hasOwnProperty.call(a,r)&&(e[r]=a[r])}return e},s.apply(this,arguments)}function o(e,t){if(null==e)return{};var a,r,n={},i=Object.keys(e);for(r=0;r<i.length;r++)t.indexOf(a=i[r])>=0||(n[a]=e[a]);return n}const c=()=>"undefined"!=typeof HTMLImageElement&&"loading"in HTMLImageElement.prototype;function l(e,t,a){const r={};let n="gatsby-image-wrapper";return"fixed"===a?(r.width=e,r.height=t):"constrained"===a&&(n="gatsby-image-wrapper gatsby-image-wrapper-constrained"),{className:n,"data-gatsby-image-wrapper":"",style:r}}function d(e,t,a,r,n){return void 0===n&&(n={}),s({},a,{loading:r,shouldLoad:e,"data-main-image":"",style:s({},n,{opacity:t?1:0})})}function u(e,t,a,r,n,i,o,c){const l={};i&&(l.backgroundColor=i,"fixed"===a?(l.width=r,l.height=n,l.backgroundColor=i,l.position="relative"):("constrained"===a||"fullWidth"===a)&&(l.position="absolute",l.top=0,l.left=0,l.bottom=0,l.right=0)),o&&(l.objectFit=o),c&&(l.objectPosition=c);const d=s({},e,{"aria-hidden":!0,"data-placeholder-image":"",style:s({opacity:t?0:1,transition:"opacity 500ms linear"},l)});return d}const g=["children"],p=function(e){let{layout:t,width:a,height:n}=e;return"fullWidth"===t?r.createElement("div",{"aria-hidden":!0,style:{paddingTop:n/a*100+"%"}}):"constrained"===t?r.createElement("div",{style:{maxWidth:a,display:"block"}},r.createElement("img",{alt:"",role:"presentation","aria-hidden":"true",src:"data:image/svg+xml;charset=utf-8,%3Csvg%20height='"+n+"'%20width='"+a+"'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E",style:{maxWidth:"100%",display:"block",position:"static"}})):null},m=function(e){let{children:t}=e,a=o(e,g);return r.createElement(r.Fragment,null,r.createElement(p,s({},a)),t,null)},b=["src","srcSet","loading","alt","shouldLoad"],f=["fallback","sources","shouldLoad"],h=function(e){let{src:t,srcSet:a,loading:n,alt:i="",shouldLoad:c}=e,l=o(e,b);return r.createElement("img",s({},l,{decoding:"async",loading:n,src:c?t:void 0,"data-src":c?void 0:t,srcSet:c?a:void 0,"data-srcset":c?void 0:a,alt:i}))},y=function(e){let{fallback:t,sources:a=[],shouldLoad:n=!0}=e,i=o(e,f);const c=i.sizes||(null==t?void 0:t.sizes),l=r.createElement(h,s({},i,t,{sizes:c,shouldLoad:n}));return a.length?r.createElement("picture",null,a.map((e=>{let{media:t,srcSet:a,type:i}=e;return r.createElement("source",{key:t+"-"+i+"-"+a,type:i,media:t,srcSet:n?a:void 0,"data-srcset":n?void 0:a,sizes:c})})),l):l};var w;h.propTypes={src:n.string.isRequired,alt:n.string.isRequired,sizes:n.string,srcSet:n.string,shouldLoad:n.bool},y.displayName="Picture",y.propTypes={alt:n.string.isRequired,shouldLoad:n.bool,fallback:n.exact({src:n.string.isRequired,srcSet:n.string,sizes:n.string}),sources:n.arrayOf(n.oneOfType([n.exact({media:n.string.isRequired,type:n.string,sizes:n.string,srcSet:n.string.isRequired}),n.exact({media:n.string,type:n.string.isRequired,sizes:n.string,srcSet:n.string.isRequired})]))};const v=["fallback"],E=function(e){let{fallback:t}=e,a=o(e,v);return t?r.createElement(y,s({},a,{fallback:{src:t},"aria-hidden":!0,alt:""})):r.createElement("div",s({},a))};E.displayName="Placeholder",E.propTypes={fallback:n.string,sources:null==(w=y.propTypes)?void 0:w.sources,alt:function(e,t,a){return e[t]?new Error("Invalid prop `"+t+"` supplied to `"+a+"`. Validation failed."):null}};const _=function(e){return r.createElement(r.Fragment,null,r.createElement(y,s({},e)),r.createElement("noscript",null,r.createElement(y,s({},e,{shouldLoad:!0}))))};_.displayName="MainImage",_.propTypes=y.propTypes;const x=["as","className","class","style","image","loading","imgClassName","imgStyle","backgroundColor","objectFit","objectPosition"],S=["style","className"],k=e=>e.replace(/\n/g,""),L=function(e,t,a){for(var r=arguments.length,n=new Array(r>3?r-3:0),s=3;s<r;s++)n[s-3]=arguments[s];return e.alt||""===e.alt?i().string.apply(i(),[e,t,a].concat(n)):new Error('The "alt" prop is required in '+a+'. If the image is purely presentational then pass an empty string: e.g. alt="". Learn more: https://a11y-style-guide.com/style-guide/section-media.html')},C={image:i().object.isRequired,alt:L},T=["as","image","style","backgroundColor","className","class","onStartLoad","onLoad","onError"],N=["style","className"],z=new Set;let I,O;const j=function(e){let{as:t="div",image:n,style:i,backgroundColor:d,className:u,class:g,onStartLoad:p,onLoad:m,onError:b}=e,f=o(e,T);const{width:h,height:y,layout:w}=n,v=l(h,y,w),{style:E,className:_}=v,x=o(v,N),S=(0,r.useRef)(),k=(0,r.useMemo)((()=>JSON.stringify(n.images)),[n.images]);g&&(u=g);const L=function(e,t,a){let r="";return"fullWidth"===e&&(r='<div aria-hidden="true" style="padding-top: '+a/t*100+'%;"></div>'),"constrained"===e&&(r='<div style="max-width: '+t+'px; display: block;"><img alt="" role="presentation" aria-hidden="true" src="data:image/svg+xml;charset=utf-8,%3Csvg%20height=\''+a+"'%20width='"+t+"'%20xmlns='http://www.w3.org/2000/svg'%20version='1.1'%3E%3C/svg%3E\" style=\"max-width: 100%; display: block; position: static;\"></div>"),r}(w,h,y);return(0,r.useEffect)((()=>{I||(I=a.e(731).then(a.bind(a,6731)).then((e=>{let{renderImageToString:t,swapPlaceholderImage:a}=e;return O=t,{renderImageToString:t,swapPlaceholderImage:a}})));const e=S.current.querySelector("[data-gatsby-image-ssr]");if(e&&c())return e.complete?(null==p||p({wasCached:!0}),null==m||m({wasCached:!0}),setTimeout((()=>{e.removeAttribute("data-gatsby-image-ssr")}),0)):(null==p||p({wasCached:!0}),e.addEventListener("load",(function t(){e.removeEventListener("load",t),null==m||m({wasCached:!0}),setTimeout((()=>{e.removeAttribute("data-gatsby-image-ssr")}),0)}))),void z.add(k);if(O&&z.has(k))return;let t,r;return I.then((e=>{let{renderImageToString:a,swapPlaceholderImage:o}=e;S.current&&(S.current.innerHTML=a(s({isLoading:!0,isLoaded:z.has(k),image:n},f)),z.has(k)||(t=requestAnimationFrame((()=>{S.current&&(r=o(S.current,k,z,i,p,m,b))}))))})),()=>{t&&cancelAnimationFrame(t),r&&r()}}),[n]),(0,r.useLayoutEffect)((()=>{z.has(k)&&O&&(S.current.innerHTML=O(s({isLoading:z.has(k),isLoaded:z.has(k),image:n},f)),null==p||p({wasCached:!0}),null==m||m({wasCached:!0}))}),[n]),(0,r.createElement)(t,s({},x,{style:s({},E,i,{backgroundColor:d}),className:_+(u?" "+u:""),ref:S,dangerouslySetInnerHTML:{__html:L},suppressHydrationWarning:!0}))},q=(0,r.memo)((function(e){return e.image?(0,r.createElement)(j,e):null}));q.propTypes=C,q.displayName="GatsbyImage";const R=["src","__imageData","__error","width","height","aspectRatio","tracedSVGOptions","placeholder","formats","quality","transformOptions","jpgOptions","pngOptions","webpOptions","avifOptions","blurredOptions","breakpoints","outputPixelDensities"];function A(e){return function(t){let{src:a,__imageData:n,__error:i}=t,c=o(t,R);return i&&console.warn(i),n?r.createElement(e,s({image:n},c)):(console.warn("Image not loaded",a),null)}}const M=A((function(e){let{as:t="div",className:a,class:n,style:i,image:c,loading:g="lazy",imgClassName:p,imgStyle:b,backgroundColor:f,objectFit:h,objectPosition:y}=e,w=o(e,x);if(!c)return console.warn("[gatsby-plugin-image] Missing image prop"),null;n&&(a=n),b=s({objectFit:h,objectPosition:y,backgroundColor:f},b);const{width:v,height:L,layout:C,images:T,placeholder:N,backgroundColor:z}=c,I=l(v,L,C),{style:O,className:j}=I,q=o(I,S),R={fallback:void 0,sources:[]};return T.fallback&&(R.fallback=s({},T.fallback,{srcSet:T.fallback.srcSet?k(T.fallback.srcSet):void 0})),T.sources&&(R.sources=T.sources.map((e=>s({},e,{srcSet:k(e.srcSet)})))),r.createElement(t,s({},q,{style:s({},O,i,{backgroundColor:f}),className:j+(a?" "+a:"")}),r.createElement(m,{layout:C,width:v,height:L},r.createElement(E,s({},u(N,!1,C,v,L,z,h,y))),r.createElement(_,s({"data-gatsby-image-ssr":"",className:p},w,d("eager"===g,!1,R,g,b)))))})),P=function(e,t){for(var a=arguments.length,r=new Array(a>2?a-2:0),n=2;n<a;n++)r[n-2]=arguments[n];return"fullWidth"!==e.layout||"width"!==t&&"height"!==t||!e[t]?i().number.apply(i(),[e,t].concat(r)):new Error('"'+t+'" '+e[t]+" may not be passed when layout is fullWidth.")},F=new Set(["fixed","fullWidth","constrained"]),W={src:i().string.isRequired,alt:L,width:P,height:P,sizes:i().string,layout:e=>{if(void 0!==e.layout&&!F.has(e.layout))return new Error("Invalid value "+e.layout+'" provided for prop "layout". Defaulting to "constrained". Valid values are "fixed", "fullWidth" or "constrained".')}};M.displayName="StaticImage",M.propTypes=W;const D=A(q);D.displayName="StaticImage",D.propTypes=W},5592:function(e,t,a){a.d(t,{Z:function(){return o}});var r=a(7294),n=a(1883),i=a(8032);var s=e=>{let{siteTitle:t}=e;return r.createElement("header",{style:{margin:"0 auto",padding:"var(--space-4) var(--size-gutter)",display:"flex",alignItems:"center",justifyContent:"space-between"}},r.createElement(n.Link,{to:"/",style:{fontSize:"var(--font-lg)",textDecoration:"none"}},r.createElement(i.S,{src:"../images/product_logo.png",placeholder:"product logo",loading:"eager",height:30,quality:95,formats:["auto","webp","avif"],alt:"",style:{margin:0},__imageData:a(7822)}),r.createElement("b",{style:{verticalAlign:"bottom"}},t)),r.createElement(i.S,{src:"../images/team_logo.png",placeholder:"team logo",loading:"eager",height:30,quality:95,formats:["auto","webp","avif"],alt:"",style:{margin:0},__imageData:a(716)}))};var o=e=>{var t;let{children:a}=e;const i=(0,n.useStaticQuery)("3649515864");return r.createElement(r.Fragment,null,r.createElement(s,{siteTitle:(null===(t=i.site.siteMetadata)||void 0===t?void 0:t.title)||"Title"}),r.createElement("div",{style:{margin:"0 auto",maxWidth:"var(--size-content)",padding:"var(--size-gutter)"}},r.createElement("main",null,a),r.createElement("footer",{style:{marginTop:"var(--space-5)",fontSize:"var(--font-sm)"}},"© ",(new Date).getFullYear()," チーム勝成 · Built with"," ",r.createElement("a",{href:"https://www.gatsbyjs.com"},"Gatsby"))))}},9357:function(e,t,a){var r=a(7294),n=a(1883);t.Z=function(e){var t,a;let{description:i,title:s,children:o}=e;const{site:c}=(0,n.useStaticQuery)("63159454"),l=i||c.siteMetadata.description,d=null===(t=c.siteMetadata)||void 0===t?void 0:t.title;return r.createElement(r.Fragment,null,r.createElement("title",null,d?s+" | "+d:s),r.createElement("meta",{name:"description",content:l}),r.createElement("meta",{property:"og:title",content:s}),r.createElement("meta",{property:"og:description",content:l}),r.createElement("meta",{property:"og:type",content:"website"}),r.createElement("meta",{name:"twitter:card",content:"summary"}),r.createElement("meta",{name:"twitter:creator",content:(null===(a=c.siteMetadata)||void 0===a?void 0:a.author)||""}),r.createElement("meta",{name:"twitter:title",content:s}),r.createElement("meta",{name:"twitter:description",content:l}),o)}},7822:function(e){e.exports=JSON.parse('{"layout":"constrained","images":{"fallback":{"src":"/static/cead9c35c2581d3788b7fe2de2cbba5c/a92f3/product_logo.png","srcSet":"/static/cead9c35c2581d3788b7fe2de2cbba5c/bf7af/product_logo.png 8w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/ccb69/product_logo.png 15w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/a92f3/product_logo.png 30w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/d6284/product_logo.png 60w","sizes":"(min-width: 30px) 30px, 100vw"},"sources":[{"srcSet":"/static/cead9c35c2581d3788b7fe2de2cbba5c/c42ee/product_logo.avif 8w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/559ff/product_logo.avif 15w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/7331c/product_logo.avif 30w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/fc876/product_logo.avif 60w","type":"image/avif","sizes":"(min-width: 30px) 30px, 100vw"},{"srcSet":"/static/cead9c35c2581d3788b7fe2de2cbba5c/70f85/product_logo.webp 8w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/10ce9/product_logo.webp 15w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/9694d/product_logo.webp 30w,\\n/static/cead9c35c2581d3788b7fe2de2cbba5c/79de8/product_logo.webp 60w","type":"image/webp","sizes":"(min-width: 30px) 30px, 100vw"}]},"width":30,"height":30}')},716:function(e){e.exports=JSON.parse('{"layout":"constrained","images":{"fallback":{"src":"/static/7a092ed6b39bf4d1e60962479a333ab5/34c0f/team_logo.png","srcSet":"/static/7a092ed6b39bf4d1e60962479a333ab5/5330b/team_logo.png 32w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/6651b/team_logo.png 64w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/34c0f/team_logo.png 128w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/50304/team_logo.png 256w","sizes":"(min-width: 128px) 128px, 100vw"},"sources":[{"srcSet":"/static/7a092ed6b39bf4d1e60962479a333ab5/bd708/team_logo.avif 32w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/cc637/team_logo.avif 64w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/25e6f/team_logo.avif 128w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/2e8ef/team_logo.avif 256w","type":"image/avif","sizes":"(min-width: 128px) 128px, 100vw"},{"srcSet":"/static/7a092ed6b39bf4d1e60962479a333ab5/84fd5/team_logo.webp 32w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/f8780/team_logo.webp 64w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/1d914/team_logo.webp 128w,\\n/static/7a092ed6b39bf4d1e60962479a333ab5/e827a/team_logo.webp 256w","type":"image/webp","sizes":"(min-width: 128px) 128px, 100vw"}]},"width":128,"height":30}')}}]);
//# sourceMappingURL=commons-d38ec29d344f08745862.js.map