const text = `{
  "executive_summary": "Line 1\nLine 2",
  "key2": "value2"
}`;

let cleanedContent = text.replace(/"([^"\\]*(?:\\.[^"\\]*)*)"/g, (match, p1) => {
  return '"' + p1.replace(/\n/g, '\\n').replace(/\r/g, '\\r').replace(/\t/g, '\\t') + '"';
});

console.log(cleanedContent);
console.log(JSON.parse(cleanedContent));
