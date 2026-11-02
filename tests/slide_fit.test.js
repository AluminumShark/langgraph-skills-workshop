// No browser required: exercise the real sizing functions across reveal states.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function node(classes = '') {
  const values = new Set(classes.split(' ').filter(Boolean));
  return {
    style: {},
    classList: { add: x => values.add(x), remove: x => values.delete(x), contains: x => values.has(x) },
    getAttribute: key => key === 'class' ? [...values].join(' ') : null,
    setAttribute(key, value) {
      if (key === 'class') { values.clear(); value.split(' ').filter(Boolean).forEach(x => values.add(x)); }
      else this[key] = value;
    },
    removeAttribute(key) { if (key === 'class') values.clear(); else delete this[key]; },
  };
}

for (const name of ['session1', 'session2']) {
  const html = fs.readFileSync(path.join(__dirname, '..', 'slides', `${name}.html`), 'utf8');
  const start = html.indexOf('  function fitSlide(s)');
  const end = html.indexOf('  function copyText(', start);
  const reveals = [node('step'), node('step'), node('step')];
  let lineHeight = 200;
  const body = { offsetTop: 0, get offsetHeight() { return 500 + reveals.filter(n => n.classList.contains('on')).length * lineHeight; } };
  const sb = { style: {}, offsetTop: 0, clientWidth: 1000, scrollWidth: 1000, children: [body], querySelectorAll: () => [] };
  const slide = node('slide active');
  slide.querySelector = selector => selector === '.sb' ? sb : { offsetTop: 812 };
  slide.querySelectorAll = () => reveals;
  const context = vm.createContext({ slides: [slide], fittedSlides: new WeakSet() });
  vm.runInContext(html.slice(start, end), context);

  context.fitSlide(slide);
  const expected = sb.style.transform;
  assert.equal(expected, 'scale(0.727)', `${name}: reserve space for every reveal`);
  assert.equal(reveals[0].classList.contains('on'), false, 'measurement must preserve current reveal state');
  reveals[0].classList.add('on');
  context.fitSlide(slide);
  assert.equal(sb.style.transform, expected, `${name}: next step must not resize`);
  reveals.forEach(n => n.classList.add('on'));
  context.fitSlide(slide);
  assert.equal(sb.style.transform, expected, `${name}: last step must not resize`);
  reveals.forEach(n => n.classList.remove('on'));
  context.fitSlide(slide);
  assert.equal(sb.style.transform, expected, `${name}: previous step must not resize`);
  lineHeight = 250; // Simulate changed font metrics, then run the resize/font hook.
  context.fitAll();
  assert.equal(sb.style.transform, 'scale(0.640)', `${name}: remeasure when layout changes`);
  console.log(`${name}: reveal sizing regression passed`);
}
