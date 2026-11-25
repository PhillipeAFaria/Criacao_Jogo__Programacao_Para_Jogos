/* Public browser UI. No accounts, trackers, redirects or desktop-save access. */
(() => {
 const KEY='fabrica-dos-mortos:web:save:v1', queue=[];
 let ready=false, busy=false, started=Date.now();
 const root=document.createElement('div'); root.id='web-ui';
 root.innerHTML=`<header><strong>FÃ¡brica dos Mortos</strong><button id="full">Tela cheia</button><button data-action="sound">Som</button><button id="export">Exportar progresso</button></header>
 <section id="loading-web" role="status"><h1>FÃ¡brica dos Mortos</h1><p id="load-label">Carregandoâ€¦ Toque aqui para habilitar o Ã¡udio.</p><progress id="load-progress" max="100"></progress><p class="hint">A primeira abertura baixa as artes do jogo. Mantenha esta pÃ¡gina aberta.</p><button id="retry" hidden>Recarregar</button></section>
 <div id="web-error" role="alert" hidden></div>
 <nav aria-label="Controles do jogo"><button data-action="menu">Voltar / Menu</button><button data-action="pause">Pausar</button><button data-action="wave">PrÃ³xima onda</button><button data-action="remove">Recolher</button><button data-action="medkit">Kit mÃ©dico</button><button data-action="ammo">MuniÃ§Ã£o</button><button data-action="info">Detalhes</button><button data-action="lab">LaboratÃ³rio</button><button data-action="save">Salvar</button></nav>
 <div id="rotate">Gire o aparelho para jogar na horizontal.</div>
 <dialog id="name-dialog"><form method="dialog"><label>Nome do jogador<input id="player-name" maxlength="20" autocomplete="nickname"></label><button value="cancel">Cancelar</button><button value="save">Salvar nome</button></form></dialog>`;
 document.body.append(root);
 // SDL listens globally and prevents native text editing. Keep DOM controls'
 // keyboard events out of the game without cancelling the browser's editing.
 for(const type of ['keydown','keypress','keyup']){
   window.addEventListener(type,e=>{
     if(e.target instanceof Element && e.target.closest('#web-ui input, #web-ui textarea, #web-ui select, #web-ui dialog')){
       e.stopImmediatePropagation();
     }
   },{capture:true});
 }
 const labDialog=document.createElement('dialog');labDialog.id='lab-dialog';
 labDialog.innerHTML='<h2>LaboratÃ³rio</h2><label>Mapa <select id="lab-region"><option value="city">Cidade</option><option value="desert">Deserto</option><option value="beach">Cachoeira</option></select></label><button id="lab-team">Trocar soldados / zumbis</button><label>Unidade <select id="lab-unit"></select></label><p>Selecione a unidade, feche e toque na pista para colocÃ¡-la.</p><button id="lab-clear">Limpar</button><button id="lab-close">Voltar ao mapa</button>';
 root.append(labDialog);let labOptions='';
 const cards=document.createElement('select');cards.id='touch-cards';cards.setAttribute('aria-label','Selecionar unidade');cards.hidden=true;
 root.querySelector('nav').prepend(cards);let cardOptions='';
 const $=id=>document.getElementById(id);
 function status(text,percent){$('load-label').textContent=text; if(percent>=0)$('load-progress').value=percent;}
 function fail(text){$('web-error').hidden=false;$('web-error').textContent=text;$('retry').hidden=false;}
 function send(action,extra={}){if(!busy||['hidden','visible'].includes(action))queue.push({action,...extra});}
 const header=root.querySelector('header'), nav=root.querySelector('nav');
 const hud=document.createElement('div');hud.id='battle-web-hud';hud.hidden=true;
 const controls=document.createElement('dialog');controls.id='battle-controls';
 controls.innerHTML='<button id="controls-close">Voltar ao jogo</button>';
 const more=document.createElement('button');more.textContent='â‹¯';more.setAttribute('aria-label','Mais controles');
 root.append(hud,controls);more.onclick=()=>controls.showModal();
 $('controls-close').onclick=()=>controls.close();
 const full=$('full'),medkit=nav.querySelector('[data-action="medkit"]'),ammo=nav.querySelector('[data-action="ammo"]');
 let battleLayout=false;
 function layout(scene){
   const active=scene==='battle';
   if(active===battleLayout)return;
   battleLayout=active;document.body.classList.toggle('battle-layout',active);hud.hidden=!active;
   controls.close();
   if(active){hud.append(full,medkit,ammo,more);controls.append(header,nav);}
   else{root.prepend(header);root.append(nav);header.insertBefore(full,header.querySelector('[data-action="sound"]'));nav.append(medkit,ammo);}
   positionHud();
 }
 function positionHud(){
   const r=document.getElementById('canvas')?.getBoundingClientRect();if(!r)return;
   // Free HUD interval: points end at x=278; next wave begins at x=790.
   hud.style.left=(r.left+r.width*290/1280)+'px';
   hud.style.top=(r.top+r.height*638/720)+'px';
   hud.style.width=(r.width*488/1280)+'px';
   hud.style.height=(r.height*76/720)+'px';
 }
 async function fullscreen(){
   if(document.fullscreenElement){await document.exitFullscreen();return;}
   if(document.body.classList.contains('immersive')){document.body.classList.remove('immersive');syncFullscreen();return;}
   try{await document.documentElement.requestFullscreen();try{await screen.orientation?.lock?.('landscape');}catch(e){}}
   catch(e){document.body.classList.add('immersive');}
   syncFullscreen();
 }
 function syncFullscreen(){
   const active=Boolean(document.fullscreenElement)||document.body.classList.contains('immersive');
   full.textContent=active?'Sair da tela':'Tela cheia';full.setAttribute('aria-pressed',String(active));
   full.title=active?'Sair da tela cheia':'Ampliar jogo em tela cheia';positionHud();
 }
 document.addEventListener('fullscreenchange',syncFullscreen);
 window.addEventListener('resize',positionHud);
 window.visualViewport?.addEventListener('resize',positionHud);
 new ResizeObserver(positionHud).observe(document.getElementById('canvas'));

 window.fdm={
   load(){return localStorage.getItem(KEY)||''},
   save(raw){try{localStorage.setItem(KEY,raw);return ''}catch(e){return e.message}},
   drain(){return JSON.stringify(queue.splice(0))},
   isHidden(){return document.hidden||matchMedia('(orientation:portrait) and (pointer:coarse)').matches},
   status,fail,fullscreen,
   statusJSON(raw,percent){status(JSON.parse(raw),percent)},
   editNameJSON(raw){window.fdm.editName(JSON.parse(raw))},
   busy(value){busy=Boolean(value);if(busy){started=Date.now();$('retry').hidden=true;}ready=!busy;$('loading-web').hidden=!busy;window.fdmBusy=busy;},
   async invalidate(url){try{const cache=await caches.open(cacheName);await cache.delete(new URL(url,location.href).href);}catch(e){}},
   async keepAssets(raw){try{const keep=new Set(JSON.parse(raw).map(u=>new URL(u,location.href).href));if(activeBootstrap)keep.add(activeBootstrap);const cache=await caches.open(cacheName);for(const request of await cache.keys())if(!keep.has(request.url))await cache.delete(request);}catch(e){}},
   editName(value){$('player-name').value=value;$('name-dialog').showModal();$('player-name').focus()},
   state(raw){const state=JSON.parse(raw);window.fdmState=state;
      layout(state.scene);
      if(state.error)fail(state.error);
      if(state.scene!=='loading'){ready=true;$('loading-web').hidden=true;}
      else status(`Preparando artes e animaÃ§Ãµes: ${state.loaded}/${state.total}`,state.loaded/state.total*100);
      document.querySelector('[data-action="lab"]').disabled=!['title','developer'].includes(state.scene);
      if(state.lab){
        $('lab-region').value=state.lab.region;
        const key=JSON.stringify(state.lab.entries);
        if(key!==labOptions){$('lab-unit').replaceChildren(...state.lab.entries.map((entry,i)=>new Option(entry[1],String(i))));labOptions=key;}
        $('lab-unit').value=String(state.lab.index);
      }
      cards.hidden=!state.cards?.length;
      const cardKey=JSON.stringify(state.cards||[]);
      if(cardOptions!==cardKey){cards.replaceChildren(...(state.cards||[]).map((name,i)=>new Option(name,String(i))));cardOptions=cardKey;}
   }
 };
 root.querySelectorAll('[data-action]').forEach(button=>button.onclick=()=>send(button.dataset.action));
 root.querySelector('[data-action="lab"]').onclick=()=>{if(window.fdmState?.scene==='developer')labDialog.showModal();else send('lab')};
 $('lab-region').onchange=()=>send('lab_action',{value:$('lab-region').value});
 $('lab-unit').onchange=()=>send('lab_action',{value:'pick:'+$('lab-unit').value});
 $('lab-team').onclick=()=>send('lab_action',{value:'team'});
 $('lab-clear').onclick=()=>send('lab_action',{value:'clear'});
 $('lab-close').onclick=()=>labDialog.close();
 cards.onchange=()=>send('card',{value:Number(cards.value)});
 $('full').onclick=fullscreen;
 $('retry').onclick=()=>location.reload();
 $('name-dialog').addEventListener('close',()=>{if($('name-dialog').returnValue==='save')send('name',{value:$('player-name').value});});
 $('export').onclick=()=>{send('save');setTimeout(()=>{
   const raw=localStorage.getItem(KEY);if(!raw){fail('Ainda nÃ£o hÃ¡ progresso salvo para exportar.');return;}
   const url=URL.createObjectURL(new Blob([raw],{type:'application/json'}));
   const a=document.createElement('a');a.href=url;a.download='fabrica-dos-mortos-progresso-web.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 },400)};
 document.addEventListener('visibilitychange',()=>send(document.hidden?'hidden':'visible'));
 window.addEventListener('pagehide',()=>send('hidden'));
 window.addEventListener('error',e=>{if(e.message)fail('Falha no carregamento: '+e.message)});
 // Pointer events map CSS-scaled canvas coordinates to the untouched 1280x720 board.
 // Stop SDL's synthesized touch/mouse events to prevent double placement.
 const canvas=document.getElementById('canvas');
 if(canvas){
   for(const type of ['pointerdown','pointerup','touchstart','touchend','mousedown','mouseup','click']){
     canvas.addEventListener(type,e=>{
       if(!ready){if(busy){e.preventDefault();e.stopImmediatePropagation();}return;}
       if(type==='pointerdown' && e.isPrimary && e.button===0){
         const r=canvas.getBoundingClientRect();send('click',{x:(e.clientX-r.left)*1280/r.width,y:(e.clientY-r.top)*720/r.height});
       }
       e.preventDefault();e.stopImmediatePropagation();
     },{capture:true,passive:false});
   }
 }
 document.addEventListener('contextmenu',e=>e.preventDefault());
 document.addEventListener('wheel',e=>{if(e.ctrlKey)e.preventDefault()},{passive:false});
 setInterval(()=>{if(!ready && Date.now()-started>120000){$('retry').hidden=false;status('O carregamento estÃ¡ demorando. Verifique a conexÃ£o e tente recarregar.',-1)}},5000);
 // Track the actual application archive download, while keeping the runtime loader intact.
 const fetchOriginal=window.fetch;
 const cacheName='fdm-assets-v1:'+location.pathname.replace(/[^/]*$/,'');
 let activeBootstrap='';
 window.fdmNetwork={hits:0,downloads:0,bytes:0};
 window.fetch=async function(input,init){
   const url=String(input),absolute=new URL(url,location.href);
   const persistent=absolute.origin===location.origin && /(?:bootstrap-[a-f0-9]+\.tar\.gz|atlas_\d+-[a-f0-9]+\.png)$/.test(absolute.pathname);
   if(persistent && absolute.pathname.includes('bootstrap-'))activeBootstrap=absolute.href;
   let cache=null,response;
   if(persistent){try{cache=await caches.open(cacheName);response=await cache.match(absolute.href);}catch(e){}}
   if(response){window.fdmNetwork.hits++;return response;}
   response=await fetchOriginal(input,init);
   if(persistent && response.ok){
     window.fdmNetwork.downloads++;window.fdmNetwork.bytes+=Number(response.headers.get('Content-Length'))||0;
     if(cache)cache.put(absolute.href,response.clone()).catch(()=>{});
   }
   if(!response.ok && persistent)throw new Error('Falha ao baixar recursos ('+response.status+'). Recarregue para tentar novamente.');
   if(!/\.(tar\.gz|apk)(\?|$)/.test(url)||!response.body)return response;
   const total=Number(response.headers.get('Content-Length')),reader=response.body.getReader();let bytes=0;
   const stream=new ReadableStream({async pull(controller){try{
     const {done,value}=await reader.read();if(done){controller.close();return;}
     bytes+=value.byteLength;status(`Baixando jogo: ${(bytes/1048576).toFixed(1)} MB${total?' / '+(total/1048576).toFixed(1)+' MB':''}`,total?bytes/total*100:-1);controller.enqueue(value);
   }catch(error){fail('NÃ£o foi possÃ­vel baixar os arquivos. Recarregue a pÃ¡gina.');controller.error(error);}}});
   return new Response(stream,{headers:response.headers,status:response.status,statusText:response.statusText});
 };
})();
