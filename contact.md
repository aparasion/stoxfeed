---
layout: page
title: Contact
permalink: /contact/
nav: false
nav_order: 8
---

<form action="https://formspree.io/f/xgoljzky"
      method="POST"
      class="contact-form">

  <div class="form-group">
    <label for="name">Name</label>
    <input type="text" name="name" id="name" required>
  </div>

  <div class="form-group">
    <label for="email">Email</label>
    <input type="email" name="email" id="email" required>
  </div>

  <div class="form-group">
    <label for="message">Message</label>
    <textarea name="message" id="message" rows="6" required></textarea>
  </div>

  <button type="submit" class="btn-submit">
    Send Message
  </button>
<input type="hidden" name="_next" value="/thank-you/">
</form>


