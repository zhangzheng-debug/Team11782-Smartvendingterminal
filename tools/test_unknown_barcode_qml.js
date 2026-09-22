// Execute the actual QML JavaScript function with UI/API doubles, not a Qt renderer.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const api = fs.readFileSync(path.join(root, 'qt_kiosk/retail_api.js'), 'utf8').replace('.pragma library', '');
const apiContext = vm.createContext({});
vm.runInContext(api, apiContext);
let sent;
apiContext.apiPost = (route, body, cb) => { sent = {route, body, cb}; };
const cb = () => {};
apiContext.visionCandidates('old.jpg', cb);
assert.equal(sent.body.capture, false);
assert.equal(sent.cb, cb);
apiContext.visionCandidates('', true, cb);
assert.equal(sent.body.capture, true);
assert.equal(sent.body.image_path, '');

const qml = fs.readFileSync(path.join(root, 'qt_kiosk/Main.qml'), 'utf8');
const start = qml.indexOf('    function submitScan(');
const end = qml.indexOf('    function routeAcceptedInput(', start);
assert.ok(start >= 0 && end > start);
for (const ok of [true, false]) {
    let refreshed = 0;
    let focused = 0;
    let previewed = 0;
    const ctx = vm.createContext({
        scanInput: {text: 'UNKNOWN_TEST_001'}, scanBuffer: '', capturePreviewPath: 'stale.jpg',
        nowClock: () => '12:00', refreshNow: () => refreshed++, ensureScannerFocus: () => focused++,
        updateCapturePreview: () => previewed++,
        RetailApi: {
            scanBarcode: (code, done) => done(false, {error_reason: 'unknown_barcode', message: '未录入商品'}),
            visionCandidates: (image, capture, done) => {
                assert.equal(image, '');
                assert.equal(capture, true);
                done(ok, {top1_name: '候选商品', message: '摄像头忙', capture: {ok}});
            },
        },
    });
    vm.runInContext(qml.slice(start, end), ctx);
    ctx.submitScan('UNKNOWN_TEST_001', 'hid');
    assert.ok(ctx.statusMessage.includes(ok ? '候选商品' : '摄像头忙'));
    assert.equal(previewed, ok ? 1 : 0);
    assert.ok(refreshed > 0 && focused > 0);
    assert.equal(ctx.scanBuffer, '');
}
console.log('PASS: legacy/new API arguments, fresh unknown capture, visible success/failure, preview, refresh and focus');
