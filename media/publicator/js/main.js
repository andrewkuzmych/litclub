function quickReply(id) {
  qrForm = document.getElementById('qr'); 
  qrForm.style.display = '';
  parentId = document.getElementById('parent');
  parentId.value = id;
  if (id == 'b' || id == 't') {
    parentId.value = 0
  } else {
    parentId.value = id
  }
  document.getElementById('qr'+id).appendChild(qrForm);
  
  // loads captcha
  captcha = document.getElementById('captcha_img');
  if (captcha) {
    if (!captcha.src) {
      captcha.src = "/captcha/" + document.getElementById('captcha_sid').value + ".gif";
      document.getElementById('captcha_img_label').style.display = '';
      captcha.onload = function(e) { document.getElementById('captcha_img_label').style.display = 'none'; };
    } 
  }
}