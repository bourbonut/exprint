const list = /(\[list\])/g;
const number = /(?<!\.)(?<!\.\s)-?\b\d+(?:\.\d+)?\b/g;
const string = /'([^']*)'/g;
const quotes = /"([^"]*)"/g;
const hlcode = document.getElementById("hlcode");
const code = (hlcode == null) ? null : hlcode.querySelector("code");
if (code != null) {
  code.querySelectorAll("span").forEach(span => {
    const replaced = span.textContent.replace(quotes, (match) => {
      return `<span class="hl-string">${match}</span>`;
    }).replace(string, (match) => {
      return `<span class="hl-string">${match}</span>`;
    }).replace(number, (match) => {
      return `<span class="hl-number">${match}</span>`;
    }).replace(list, (match) => {
      return `<span class="hl-list">${match}</span>`;
    });
    span.innerHTML = replaced;
  });
}
