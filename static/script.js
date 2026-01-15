function translateText(){
 fetch("/translate",{method:"POST",
 body:new URLSearchParams({
  text:inputText.value,
  language:language.value
 })}).then(r=>r.json()).then(d=>{
  outputText.value=d.translated
 })
}

function speakText(){
 fetch("/speak",{method:"POST",
 body:new URLSearchParams({
  text:outputText.value,
  language:language.value
 })}).then(r=>r.json()).then(d=>{
  new Audio(d.audio).play()
 })
}

function translateImage(){
 let fd=new FormData()
 fd.append("image",imageInput.files[0])
 fd.append("language",language.value)

 fetch("/image-text",{method:"POST",body:fd})
 .then(r=>r.json()).then(d=>{
  inputText.value=d.text
  outputText.value=d.translated
 })
}

function imageVoice(){
 fetch("/image-voice",{method:"POST",
 body:new URLSearchParams({
  text:outputText.value,
  language:language.value
 })}).then(r=>r.json()).then(d=>{
  new Audio(d.audio).play()
 })
}

function clearAll(){
 inputText.value=""
 outputText.value=""
 imageInput.value=""
}
