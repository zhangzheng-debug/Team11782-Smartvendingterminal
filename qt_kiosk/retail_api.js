.pragma library

var baseUrl = "http://127.0.0.1:5000";

function setBaseUrl(url) {
    baseUrl = (url || "http://127.0.0.1:5000").replace(/\/+$/, "");
}

function parseJson(text) {
    try {
        return JSON.parse(text || "{}");
    } catch (e) {
        return { ok: false, error: "bad_json", message: String(e), raw: text };
    }
}

function apiGet(path, callback) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = 8000;
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var data = parseJson(xhr.responseText);
            callback(xhr.status >= 200 && xhr.status < 300 && data.ok !== false, data, xhr.status);
        }
    };
    xhr.onerror = function() { callback(false, { ok: false, error: "network_error", message: "API request failed" }, xhr.status || 0); };
    xhr.ontimeout = function() { callback(false, { ok: false, error: "timeout", message: "API request timeout" }, 0); };
    xhr.open("GET", baseUrl + path);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.send();
}

function apiPost(path, body, callback) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = 12000;
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var data = parseJson(xhr.responseText);
            callback(xhr.status >= 200 && xhr.status < 300 && data.ok !== false, data, xhr.status);
        }
    };
    xhr.onerror = function() { callback(false, { ok: false, error: "network_error", message: "API request failed" }, xhr.status || 0); };
    xhr.ontimeout = function() { callback(false, { ok: false, error: "timeout", message: "API request timeout" }, 0); };
    xhr.open("POST", baseUrl + path);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(body || {}));
}

function apiPostTimeout(path, body, timeoutMs, callback) {
    var xhr = new XMLHttpRequest();
    xhr.timeout = timeoutMs || 12000;
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            var data = parseJson(xhr.responseText);
            callback(xhr.status >= 200 && xhr.status < 300 && data.ok !== false, data, xhr.status);
        }
    };
    xhr.onerror = function() { callback(false, { ok: false, error: "network_error", message: "API request failed" }, xhr.status || 0); };
    xhr.ontimeout = function() { callback(false, { ok: false, error: "timeout", message: "API request timeout" }, 0); };
    xhr.open("POST", baseUrl + path);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(body || {}));
}

function refreshState(callback) {
    apiGet("/api/state", callback);
}

function scanBarcode(barcode, callback) {
    apiPost("/api/scan", { barcode: barcode }, callback);
}

function addProduct(productId, callback) {
    apiPost("/api/cart/add", { product_id: productId, quantity: 1 }, callback);
}

function removeLast(callback) {
    apiPost("/api/cart/remove_last", {}, callback);
}

function removeProduct(productId, callback) {
    apiPost("/api/cart/remove_product", { product_id: productId }, callback);
}

function clearCart(callback) {
    apiPost("/api/cart/clear", {}, callback);
}

function checkout(callback) {
    apiPost("/api/checkout", {}, callback);
}

function capture(callback) {
    apiPost("/api/capture", {}, callback);
}

function cleanupCaptures(callback) {
    apiPost("/api/captures/cleanup", {}, callback);
}

function visionStatus(callback) {
    apiGet("/api/vision/status", callback);
}

function visionPredict(imagePath, callback) {
    apiPost("/api/vision/predict", { image_path: imagePath || "" }, callback);
}

function visionVerifyScan(barcode, imagePath, capture, callback) {
    if (typeof capture === "function") {
        callback = capture;
        capture = false;
    }
    apiPost("/api/vision/verify_scan", { barcode: barcode, image_path: imagePath || "", capture: !!capture }, callback);
}

function visionCandidates(imagePath, capture, callback) {
    if (typeof capture === "function") {
        callback = capture;
        capture = false;
    }
    apiPost("/api/vision/candidates", { image_path: imagePath || "", capture: !!capture, limit: 3 }, callback);
}

function visionConfirm(productId, callback) {
    apiPost("/api/vision/confirm", { product_id: productId, confirmed: true }, callback);
}

function playAudio(event, callback) {
    apiPost("/api/audio/test_output", { event: event }, callback);
}

function executeSpeech(text, confirmed, callback) {
    apiPost("/api/speech/execute", { text: text, confirmed: !!confirmed }, callback);
}

function autoSpeechOnce(callback) {
    apiPostTimeout("/api/speech/auto_once", { seconds: 3, execute: "0" }, 22000, callback);
}

function speechMenu(callback) {
    apiGet("/api/speech/menu", callback);
}

function speechCancel(callback) {
    apiPost("/api/speech/cancel", {}, callback);
}

function speechSessionStep(body, callback) {
    apiPostTimeout("/api/speech/session_step", body || {}, 24000, callback);
}

function speechButtonWake(callback) {
    apiPostTimeout("/api/speech/session_step", { button_wake: true }, 24000, callback);
}

function speechGuardStart(callback) {
    apiPost("/api/speech/guard/start", {}, callback);
}

function speechGuardStop(callback) {
    apiPost("/api/speech/guard/stop", {}, callback);
}

function speechGuardStatus(callback) {
    apiGet("/api/speech/guard/status", callback);
}

function speechGuardTick(callback) {
    apiPostTimeout("/api/speech/guard/tick", {}, 24000, callback);
}

function speechGuardCleanup(callback) {
    apiPost("/api/speech/guard/cleanup", {}, callback);
}

function regeneratePaymentQr(orderId, callback) {
    apiPost("/api/payment/qr/regenerate", { order_id: orderId || "" }, callback);
}

function cloudStatus(callback) {
    apiGet("/api/cloud/status", callback);
}

function promoteOrderCloud(orderId, callback) {
    apiPost("/api/order/" + encodeURIComponent(orderId || "") + "/promote_cloud", {}, callback);
}

function syncOrderCloud(orderId, callback) {
    apiPost("/api/order/" + encodeURIComponent(orderId || "") + "/sync_cloud", {}, callback);
}

function syncLatestPayment(callback) {
    apiPost("/api/payment/sync_latest", {}, callback);
}
