import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import "components"
import "retail_api.js" as RetailApi

ApplicationWindow {
    id: app
    visible: true
    visibility: Window.FullScreen
    width: 1280
    height: 720
    color: "#F1F5F9"
    title: "QSM368ZP-WF 智能零售终端"
    font.family: cjkFont.name || "Noto Sans SC"

    property bool compactUi: width <= 2000 || height <= 1150
    property real uiScale: compactUi ? 0.78 : 1.0
    property int pageMargin: compactUi ? 10 : 16
    property int pageGap: compactUi ? 10 : 18
    property int headerHeight: compactUi ? 78 : 92
    property int voiceHintHeight: compactUi ? 64 : 88
    property int scanBarHeight: compactUi ? 70 : 92
    property int actionBarHeight: compactUi ? 82 : 104
    property int statusBarHeight: compactUi ? 46 : 58
    property int contentWidth: Math.max(960, width - pageMargin * 2)
    property int bodyHeightHint: Math.max(520, height - headerHeight - voiceHintHeight - scanBarHeight - actionBarHeight - statusBarHeight - pageMargin * 2)
    property int cartPanelWidth: Math.max(compactUi ? 590 : 680, Math.min(compactUi ? 720 : 820, Math.round(contentWidth * (compactUi ? 0.36 : 0.39))))
    property int leftPanelWidth: Math.max(720, contentWidth - cartPanelWidth - pageGap)
    property int recognitionPanelHeight: Math.max(compactUi ? 390 : 430, Math.min(compactUi ? 450 : 560, Math.round(bodyHeightHint * (compactUi ? 0.62 : 0.58))))
    property int previewWidth: Math.max(compactUi ? 330 : 500, Math.min(compactUi ? 440 : 620, Math.round(leftPanelWidth * (compactUi ? 0.39 : 0.42))))

    function scaled(v) { return Math.max(10, Math.round(v * uiScale)); }

    property var state: ({ cart: { items: [], count: 0, total_text: "¥0.00" }, products: [], quick_products: [] })
    property bool online: false
    property bool busy: false
    property bool captureBusy: false
    property bool speechBusy: false
    property string statusMessage: "正在启动"
    property string captureMessage: ""
    property string capturePreviewSource: ""
    property string loadingPreviewSource: ""
    property string pendingPreviewSource: ""
    property string pendingPreviewPath: ""
    property string pendingPreviewKey: ""
    property string lastCaptureKey: ""
    property string capturePreviewPath: ""
    property bool capturePreviewFailed: false
    property string scanBuffer: ""
    property string recentScanRaw: "-"
    property string recentScanStatus: "等待"
    property string recentScanResult: "等待扫码"
    property string recentScanTime: "-"
    property string recentScanError: ""
    property string recentRoute: "scan"
    property string inputModeText: "扫码优先"
    property string recentSpeechCommand: "-"
    property string visionMessage: "RKNN 视觉待触发"
    property string voiceMode: "idle"
    property string voicePrompt: "先说：小售小售"
    property string voiceRawText: "-"
    property string voiceDigit: "-"
    property string voiceIntent: "-"
    property string voiceSessionMessage: "语音操作待唤醒"
    property bool voiceGuardEnabled: false
    property bool voiceGuardTickBusy: false
    property string voiceGuardStatus: "off"
    property string voiceGuardMessage: "语音守候未开启"

    FontLoader {
        id: cjkFont
        source: "file:///userdata/qt5/share/fonts/NotoSansSC-VF.ttf"
    }

    ListModel { id: quickProductModel }
    ListModel { id: cartItemModel }

    Component.onCompleted: {
        refreshNow();
        RetailApi.playAudio("system_ready", function(ok, data) {
            statusMessage = ok ? "系统已启动" : "系统启动，播报失败";
            refreshNow();
        });
        ensureScannerFocus();
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: refreshNow()
    }

    Timer {
        id: scannerRefocusTimer
        interval: 80
        repeat: false
        onTriggered: {
            if (app.visible && !speechInput.activeFocus && !scanInput.activeFocus) {
                scannerCaptureInput.forceActiveFocus();
            }
        }
    }

    Timer {
        id: voiceGuardTimer
        interval: 2600
        running: voiceGuardEnabled
        repeat: true
        onTriggered: runVoiceGuardTick()
    }

    TextInput {
        id: scannerCaptureInput
        visible: false
        focus: true
        Component.onCompleted: forceActiveFocus()
        onActiveFocusChanged: {
            if (!activeFocus && app.visible && !speechInput.activeFocus && !scanInput.activeFocus) {
                scannerRefocusTimer.restart();
            }
        }
        Keys.priority: Keys.BeforeItem
        Keys.onPressed: {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                submitScan(scanBuffer, "hid");
                event.accepted = true;
            } else if (event.key === Qt.Key_Backspace) {
                scanBuffer = scanBuffer.substring(0, Math.max(0, scanBuffer.length - 1));
                event.accepted = true;
            } else if (event.key === Qt.Key_Escape) {
                scanBuffer = "";
                event.accepted = true;
            } else if (event.text && event.text.length > 0 && !(event.modifiers & Qt.ControlModifier) && !(event.modifiers & Qt.AltModifier)) {
                scanBuffer += event.text;
                recentScanRaw = scanBuffer;
                recentScanStatus = "输入中";
                recentScanResult = "扫码输入中";
                recentScanTime = nowClock();
                event.accepted = true;
            }
        }
    }

    function nowClock() {
        var d = new Date();
        function pad(v) { return v < 10 ? "0" + v : "" + v; }
        return pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
    }

    function yuanText(v) {
        var n = Number(v || 0);
        return "¥" + n.toFixed(2);
    }

    function ensureScannerFocus() {
        scannerRefocusTimer.restart();
    }

    function scannerFocusText() {
        return scannerCaptureInput.activeFocus ? "扫码焦点：就绪" : "扫码焦点：恢复中";
    }

    function paymentStatusText() {
        var s = state.latest_order && state.latest_order.payment_status ? state.latest_order.payment_status : "idle";
        if (s === "unpaid") return "待支付";
        if (s === "paid") return "已支付";
        if (s === "idle") return "空闲";
        return s;
    }

    function speechIntentText() {
        return (state.latest_speech_parsed && state.latest_speech_parsed.intent) || "-";
    }

    function speechCorrectionText() {
        var p = state.latest_speech_parsed || {};
        var reason = String(p.reason || p.matched_pattern || "");
        var corrected = reason.indexOf("fuzzy") >= 0 || reason.indexOf("eval") >= 0 || reason.indexOf("correction") >= 0;
        return corrected ? "纠错：命中" : "纠错：未命中";
    }

    function speechConfirmText() {
        var p = state.latest_speech_parsed || {};
        return p.confirm_required ? "需要确认" : "无需确认";
    }

    function top3Text() {
        var v = state.latest_vision || {};
        var cs = v.candidates || [];
        if (!cs.length) return "Top-3：暂无";
        var out = [];
        for (var i = 0; i < Math.min(3, cs.length); i++) {
            var c = cs[i];
            out.push((c.product_id || "-") + " " + (c.product_name || "") + " " + referenceScoreText(c.confidence));
        }
        return "Top-3：" + out.join(" / ");
    }

    function referenceScoreText(conf) {
        if (conf === undefined || conf === null || conf === "") return "视觉参考";
        var n = Number(conf);
        if (!isFinite(n) || n < 0) return "视觉参考";
        return "参考分：" + Math.max(0, Math.round(n * 100)) + "%";
    }

    function visionReferenceText() {
        var sku = state.latest_vision_top1_product_id || "-";
        var v = state.latest_vision || {};
        var name = state.latest_vision_top1_product_name || v.top1_product_name || "";
        return "视觉参考：" + sku + (name ? (" " + name) : "");
    }

    function visionLatencyText() {
        var ms = state.latest_vision_latency_ms;
        if (ms === undefined || ms === null || ms === "") return "耗时：-";
        return "耗时：" + ms + " ms";
    }

    function visionConclusionText() {
        var result = state.latest_vision_result || state.latest_vision_job_status || "-";
        var match = state.latest_vision_match_scan;
        if (String(match) === "true") return "结论：与扫码结果一致";
        if (String(match) === "false") return "结论：建议复核";
        if (result === "-" || result === "idle") return "结论：仅作辅助参考";
        return "结论：" + result;
    }

    function voiceMenuCardsModel() {
        var menu = (state && state.voice_menu) ? state.voice_menu : {};
        var items = menu.items || [];
        if (items.length > 0) return items;
        return [
            { digit: "1", label: "查询总价", recommended_phrase: "小售小售一号查询总价", button_phrase: "一号查询总价" },
            { digit: "2", label: "删除上一件", recommended_phrase: "小售小售二号删除上一件", button_phrase: "二号删除上一件" },
            { digit: "3", label: "清空购物车", recommended_phrase: "小售小售三号清空购物车", button_phrase: "三号清空购物车" },
            { digit: "4", label: "结账", recommended_phrase: "小售小售四号结账", button_phrase: "四号结账" },
            { digit: "5", label: "拍照识别", recommended_phrase: "小售小售五号拍照识别", button_phrase: "五号拍照识别" },
            { digit: "0", label: "取消", recommended_phrase: "小售小售零号取消", button_phrase: "零号取消" }
        ];
    }

    function confidenceBand(conf) {
        var pct = Number(conf || 0) * 100;
        if (pct >= 80) return "视觉辅助校验：高参考分";
        if (pct >= 50) return "视觉参考分：中等，请结合扫码";
        return "视觉参考分：仅作辅助参考";
    }

    function confidenceColor(conf) {
        var pct = Number(conf || 0) * 100;
        if (pct >= 80) return "#16A34A";
        if (pct >= 50) return "#B45309";
        return "#2563EB";
    }

    function cartTotalText() {
        var cents = Number(state.cart_total_cent !== undefined ? state.cart_total_cent : ((state.cart && state.cart.total_cent) || 0));
        return "¥" + (cents / 100.0).toFixed(2);
    }

    function cartForPanel() {
        var c = state.cart || {};
        return {
            items: state.cart_items || c.items || [],
            count: Number(state.cart_count !== undefined ? state.cart_count : (c.count || 0)),
            total_cent: Number(state.cart_total_cent !== undefined ? state.cart_total_cent : (c.total_cent || 0)),
            total_text: cartTotalText()
        };
    }

    function updateCapturePreview(data) {
        var path = (data && (data.thumb_path || data.latest_capture_thumb || data.image_path || data.latest_capture)) ||
                (state.latest_capture_thumb || state.latest_capture || "");
        var url = (data && (data.thumb_url || data.latest_capture_thumb_url || data.image_url || data.latest_capture_url)) ||
                (state.latest_capture_thumb_url || state.latest_capture_url || "");
        var key = (data && (data.capture_id || data.latest_capture_id)) || state.latest_capture_id || path;
        if (path) capturePreviewPath = path;
        if (url && key && key !== lastCaptureKey && key !== pendingPreviewKey) {
            pendingPreviewPath = path;
            pendingPreviewKey = key;
            pendingPreviewSource = url + (url.indexOf("?") >= 0 ? "&" : "?") + "t=" + Date.now();
            loadingPreviewSource = pendingPreviewSource;
        }
    }

    function rebuildModels(data) {
        var products = data.quick_products || data.products || [];
        quickProductModel.clear();
        for (var i = 0; i < products.length; i++) {
            var p = products[i];
            if (!p || !p.product_id) continue;
            quickProductModel.append({
                product_id: String(p.product_id || ""),
                product_name: String(p.product_name || p.product_id || ""),
                short_name: String(p.short_name || p.product_name || p.product_id || ""),
                price_text: String(p.price_text || yuanText(p.price_yuan) || ""),
                price_cent: Number(p.price_cent || 0),
                barcode: String(p.barcode || "")
            });
        }

        var items = data.cart_items || (data.cart && data.cart.items ? data.cart.items : []);
        cartItemModel.clear();
        for (var j = 0; j < items.length; j++) {
            var item = items[j];
            cartItemModel.append({
                product_id: String(item.product_id || ""),
                product_name: String(item.product_name || item.product_id || ""),
                unit_price_text: String(item.unit_price_text || ""),
                quantity: Number(item.quantity || 0),
                subtotal_text: String(item.subtotal_text || "")
            });
        }
    }

    function actionStatus(ok, data, fallback) {
        if (!ok && data && data.error === "cart_empty") return "购物车为空，无法结账";
        if (ok) return fallback || (data && (data.message || data.result || data.status)) || "操作成功";
        return (data && (data.message || data.error || data.status)) || fallback || "操作失败";
    }

    function setResult(ok, data, fallback) {
        online = ok || (data && data.ok !== undefined);
        statusMessage = actionStatus(ok, data, fallback);
        refreshNow();
        ensureScannerFocus();
    }

    function refreshNow() {
        RetailApi.refreshState(function(ok, data, status) {
            online = ok;
            if (ok) {
                state = data;
                voiceMode = data.voice_mode || "idle";
                voicePrompt = data.voice_prompt || (data.voice_menu && data.voice_menu.command_prompt) || "先说：小售小售";
                voiceRawText = data.latest_voice_session_raw_text || "-";
                voiceDigit = data.latest_voice_session_digit || "-";
                voiceIntent = data.latest_voice_session_intent || "-";
                voiceSessionMessage = data.latest_voice_session_message || voicePrompt;
                voiceGuardEnabled = !!data.voice_guard_enabled;
                voiceGuardStatus = data.voice_guard_status || "off";
                voiceGuardMessage = data.voice_guard_message || "";
                rebuildModels(data);
                updateCapturePreview(data);
                visionMessage = (data.latest_vision_backend || data.active_backend || "-") + " / " +
                        (data.latest_vision_job_status || data.latest_vision_result || "-") + " / " +
                        (data.latest_vision_top1_product_id || "-") + " " +
                        referenceScoreText(data.latest_vision_confidence) + " / " +
                        (data.latest_vision_latency_ms || 0) + " ms";
                if (!busy && !captureBusy && !speechBusy && statusMessage.indexOf("失败") < 0 && statusMessage.indexOf("错误") < 0) {
                    if (!statusMessage || statusMessage === "正在启动" || statusMessage === "正在刷新") statusMessage = "就绪";
                }
            } else {
                statusMessage = "API 请求失败 " + status;
            }
        });
    }

    function runVisionPredict(imagePath) {
        visionMessage = "RKNN 正在识别";
        RetailApi.visionPredict(imagePath || capturePreviewPath, function(ok, data) {
            if (ok) {
                visionMessage = (data.backend || "-") + " / " + (data.top1_product_id || "-") + " " +
                        referenceScoreText(data.confidence) + " / " + (data.latency_ms || 0) + " ms";
                statusMessage = "拍照完成，视觉参考 Top-3 已更新，请人工确认";
            } else {
                visionMessage = "视觉识别失败：" + ((data && (data.message || data.error)) || "未知错误");
            }
            refreshNow();
            ensureScannerFocus();
        });
    }

    function submitScan(raw, sourceName) {
        var code = String(raw || "").trim();
        if (!code) {
            statusMessage = "扫码内容为空";
            recentScanRaw = "-";
            recentScanStatus = "empty";
            recentScanResult = "扫码内容为空";
            recentScanError = "empty";
            recentScanTime = nowClock();
            scanBuffer = "";
            ensureScannerFocus();
            return;
        }
        busy = true;
        recentRoute = sourceName || "scan";
        recentScanRaw = code;
        recentScanStatus = "提交中";
        recentScanResult = "提交中";
        recentScanError = "";
        recentScanTime = nowClock();
        statusMessage = "正在扫码/加购：" + code;
        RetailApi.scanBarcode(code, function(ok, data) {
            busy = false;
            scanInput.text = "";
            scanBuffer = "";
            var product = data && data.product ? data.product : {};
            var name = product.product_name || data.product_name || code;
            var reason = data && (data.error_reason || data.error || data.status) ? (data.error_reason || data.error || data.status) : "";
            var message = data && data.message ? data.message : "";
            if (ok) {
                recentScanStatus = "success";
                recentScanResult = "扫码成功：" + name;
                recentScanError = "";
                statusMessage = "已加入：" + name + "，正在视觉校验";
                RetailApi.visionVerifyScan(code, "", true, function(vok, vdata) {
                    if (vok) {
                        var match = String(vdata.match_scan || "");
                        if (match === "true") {
                            visionMessage = "与扫码结果一致，完成辅助校验 / " + referenceScoreText(vdata.confidence);
                        } else if (match === "false") {
                            visionMessage = "视觉参考结果不同，建议复核 / " + (vdata.top1_product_id || "-");
                        } else {
                            visionMessage = "视觉参考 Top-3 已更新，仅作辅助参考 / " + (vdata.top1_product_id || "-");
                        }
                        updateCapturePreview(vdata.capture || {});
                    } else {
                        visionMessage = "扫码视觉校验失败：" + ((vdata && (vdata.message || vdata.error)) || "未知错误");
                    }
                    refreshNow();
                    ensureScannerFocus();
                });
            } else if (reason === "unknown_barcode") {
                recentScanStatus = "unknown";
                recentScanResult = message || ("未录入商品：" + code);
                recentScanError = recentScanResult;
                statusMessage = recentScanResult + "，请查看视觉候选";
                RetailApi.visionCandidates(capturePreviewPath, function(vok, vdata) {
                    visionMessage = vok ? ("未知条码，已给出视觉候选：" + (vdata.top1_product_id || "-") + "，请确认后加入") : "未知条码候选失败";
                    refreshNow();
                    ensureScannerFocus();
                });
            } else if (reason === "empty_scan") {
                recentScanStatus = "empty";
                recentScanResult = message || "扫码内容为空";
                recentScanError = recentScanResult;
                statusMessage = recentScanResult;
            } else if (reason === "duplicate_barcode") {
                recentScanStatus = "duplicate";
                recentScanResult = message || ("重复扫码已忽略：" + code);
                recentScanError = recentScanResult;
                statusMessage = recentScanResult;
            } else {
                recentScanStatus = "error";
                recentScanResult = message || reason || "扫码失败";
                recentScanError = recentScanResult;
                statusMessage = "扫码失败：" + recentScanResult;
            }
            recentScanTime = nowClock();
            refreshNow();
            ensureScannerFocus();
        });
    }

    function routeAcceptedInput(text, sourceName) {
        var raw = String(text || "").trim();
        recentSpeechCommand = raw || "-";
        if (!raw) {
            statusMessage = "输入为空";
            ensureScannerFocus();
            return;
        }
        if (/^SKU\d{3}$/i.test(raw) || /^[0-9]{5,}$/.test(raw) || raw.indexOf("UNKNOWN") === 0) {
            recentRoute = "scan";
            inputModeText = "检测到条码，已转为扫码";
            speechInput.text = "";
            scanInput.text = "";
            submitScan(raw, sourceName || "arbitration");
        } else {
            recentRoute = "speech";
            submitSpeech(raw);
        }
    }

    function submitSpeech(text) {
        var speechText = String(text || "").trim();
        if (!speechText) {
            statusMessage = "语音命令为空";
            ensureScannerFocus();
            return;
        }
        speechBusy = true;
        recentSpeechCommand = speechText;
        statusMessage = "正在解析语音命令";
        RetailApi.executeSpeech(speechText, false, function(ok, data) {
            speechBusy = false;
            if (data.confirm_required) {
                confirmDialog.actionName = "speech";
                confirmDialog.message = "确认执行语音命令：" + data.intent + "？";
                confirmDialog.open();
            }
            setResult(ok, data, ok ? ("语音意图：" + (data.intent || "-")) : "语音命令失败");
            ensureScannerFocus();
        });
    }

    function updateVoiceSessionFromData(data) {
        if (!data) return;
        voiceMode = data.voice_mode || data.next_voice_mode || voiceMode;
        voicePrompt = (data.menu && data.menu.command_prompt) || data.message || voicePrompt;
        voiceRawText = data.text || data.latest_voice_session_raw_text || voiceRawText || "-";
        voiceDigit = data.digit || (data.numeric && data.numeric.digit) || voiceDigit || "-";
        voiceIntent = data.intent || (data.numeric && data.numeric.intent) || voiceIntent || "-";
        voiceSessionMessage = data.message || (data.action_result && data.action_result.message) || voicePrompt;
        handleUiAction(data);
        if (data.action_result && data.action_result.cart) refreshNow();
    }

    function paymentOrderFromResult(data) {
        if (!data) return null;
        if (data.order) return data.order;
        if (data.action_result && data.action_result.order) return data.action_result.order;
        if (data.exec_result && data.exec_result.order) return data.exec_result.order;
        return null;
    }

    function uiActionFromResult(data) {
        if (!data) return "";
        if (data.ui_action) return data.ui_action;
        if (data.action_result && data.action_result.ui_action) return data.action_result.ui_action;
        if (data.exec_result && data.exec_result.ui_action) return data.exec_result.ui_action;
        return "";
    }

    function openPaymentDialog(order) {
        if (!order || !order.order_id) {
            statusMessage = "订单信息不完整，无法打开支付窗口";
            return false;
        }
        paymentDialog.order = order;
        paymentDialog.open();
        return true;
    }

    function handleUiAction(data) {
        var action = uiActionFromResult(data);
        if (action === "open_payment_dialog") {
            var order = paymentOrderFromResult(data);
            if (order && openPaymentDialog(order)) {
                statusMessage = "订单已生成，请扫码支付";
                return true;
            }
            statusMessage = "订单已生成，但支付窗口缺少订单数据，请刷新";
            refreshNow();
            return false;
        }
        if (action === "show_error" && data && data.message) {
            statusMessage = data.message;
        }
        return false;
    }

    function startVoiceSession() {
        if (speechBusy) {
            statusMessage = "语音正在处理中，请稍后";
            ensureScannerFocus();
            return;
        }
        speechBusy = true;
        statusMessage = "已手动唤醒，请说完整短句，例如：四号结账";
        voiceSessionMessage = "已手动唤醒，请说完整短句，例如：四号结账";
        RetailApi.speechButtonWake(function(ok, data) {
            speechBusy = false;
            updateVoiceSessionFromData(data);
            if (ok && data.stage === "command") {
                statusMessage = data.message || "语音指令已处理";
            } else if (ok && data.voice_mode === "command_listening") {
                statusMessage = "已唤醒，请说完整短句，例如：四号结账";
            } else {
                statusMessage = (data && data.message) ? data.message : "语音指令失败，请重试";
            }
            refreshNow();
            ensureScannerFocus();
        });
    }

    function cancelVoiceSession() {
        RetailApi.speechCancel(function(ok, data) {
            updateVoiceSessionFromData(data);
            setResult(ok, data, ok ? "语音会话已取消" : "取消语音会话失败");
        });
    }

    function startVoiceGuard() {
        RetailApi.speechGuardStart(function(ok, data) {
            voiceGuardEnabled = ok && data.voice_guard_enabled;
            voiceGuardStatus = data.voice_guard_status || "listening_wake";
            voiceGuardMessage = data.voice_guard_message || "正在守候：请说小售小售";
            statusMessage = voiceGuardMessage;
            refreshNow();
            ensureScannerFocus();
        });
    }

    function stopVoiceGuard() {
        RetailApi.speechGuardStop(function(ok, data) {
            voiceGuardEnabled = false;
            voiceGuardStatus = data.voice_guard_status || "off";
            voiceGuardMessage = data.voice_guard_message || "语音守候已停止";
            statusMessage = voiceGuardMessage;
            refreshNow();
            ensureScannerFocus();
        });
    }

    function runVoiceGuardTick() {
        if (!voiceGuardEnabled || voiceGuardTickBusy || speechBusy) return;
        voiceGuardTickBusy = true;
        voiceGuardMessage = "监听中 / 识别中";
        RetailApi.speechGuardTick(function(ok, data) {
            voiceGuardTickBusy = false;
            voiceGuardEnabled = !!(data && data.voice_guard_enabled);
            voiceGuardStatus = (data && data.voice_guard_status) || voiceGuardStatus;
            voiceGuardMessage = (data && data.voice_guard_message) || (data && data.message) || voiceGuardMessage;
            updateVoiceSessionFromData(data);
            if (data && data.executed) statusMessage = data.message || "语音守候指令已执行";
            refreshNow();
            ensureScannerFocus();
        });
    }

    function doScan() {
        submitScan(scanInput.text, "manual");
    }

    function doCheckout() {
        busy = true;
        statusMessage = "正在结账";
        RetailApi.checkout(function(ok, data) {
            busy = false;
            if (ok) {
                openPaymentDialog(data.order || data);
            }
            setResult(ok, data, ok ? "订单已生成" : "结账失败");
            ensureScannerFocus();
        });
    }

    function doClearCart() {
        confirmDialog.actionName = "clear";
        confirmDialog.message = "确认清空当前购物车？";
        confirmDialog.open();
    }

    function executeConfirmedAction() {
        confirmDialog.close();
        if (confirmDialog.actionName === "clear") {
            busy = true;
            statusMessage = "正在清空购物车";
            RetailApi.clearCart(function(ok, data) {
                busy = false;
                setResult(ok, data, ok ? "购物车已清空" : "清空失败");
                ensureScannerFocus();
            });
        } else if (confirmDialog.actionName === "speech") {
            speechBusy = true;
            statusMessage = "正在执行语音命令";
            RetailApi.executeSpeech(speechInput.text, true, function(ok, data) {
                speechBusy = false;
                handleUiAction(data);
                setResult(ok, data, ok ? "语音命令已执行" : "语音命令失败");
                ensureScannerFocus();
            });
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        HeaderBar {
            Layout.fillWidth: true
            Layout.preferredHeight: app.headerHeight
            compact: app.compactUi
            terminalId: state.terminal_id || "QSM368ZP-WF-001"
            clockText: state.time || "--"
            online: app.online
            paymentStatus: paymentStatusText()
        }

        PersistentVoiceHintBar {
            Layout.fillWidth: true
            Layout.preferredHeight: app.voiceHintHeight
            compact: app.compactUi
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: app.pageMargin
            spacing: app.pageGap

            ColumnLayout {
                Layout.fillHeight: true
                Layout.preferredWidth: app.leftPanelWidth
                Layout.minimumWidth: 700
                Layout.maximumWidth: app.contentWidth - app.cartPanelWidth - app.pageGap
                spacing: app.compactUi ? 10 : 18

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: app.recognitionPanelHeight
                    radius: 6
                    color: "#FFFFFF"
                    border.color: "#CBD5E1"
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: app.compactUi ? 10 : 18
                        spacing: app.compactUi ? 10 : 18

                        Rectangle {
                            Layout.preferredWidth: app.previewWidth
                            Layout.fillHeight: true
                            radius: 6
                            color: "#0F172A"
                            Image {
                                id: capturePreview
                                anchors.fill: parent
                                anchors.margins: 8
                                fillMode: Image.PreserveAspectFit
                                cache: false
                                source: capturePreviewSource
                                onStatusChanged: {
                                    if (status === Image.Error) capturePreviewFailed = true;
                                    else if (status === Image.Ready) capturePreviewFailed = false;
                                }
                            }
                            Image {
                                id: capturePreloader
                                visible: false
                                cache: false
                                source: loadingPreviewSource
                                onStatusChanged: {
                                    if (status === Image.Ready && loadingPreviewSource.length > 0) {
                                        capturePreviewSource = loadingPreviewSource;
                                        capturePreviewPath = pendingPreviewPath;
                                        lastCaptureKey = pendingPreviewKey;
                                        loadingPreviewSource = "";
                                        pendingPreviewSource = "";
                                        capturePreviewFailed = false;
                                    } else if (status === Image.Error && loadingPreviewSource.length > 0) {
                                        loadingPreviewSource = "";
                                        pendingPreviewSource = "";
                                        capturePreviewFailed = capturePreviewSource.length === 0;
                                        statusMessage = "新图片加载失败，保留上一张预览";
                                    }
                                }
                            }
                            Text {
                                anchors.centerIn: parent
                                width: parent.width - 36
                                visible: !capturePreviewSource || capturePreviewFailed
                                text: capturePreviewFailed ? ("拍照成功但图片加载失败\n" + capturePreviewPath) : "暂无拍照"
                                color: "#CBD5E1"
                                font.pixelSize: app.compactUi ? 24 : 34
                                font.family: app.font.family
                                wrapMode: Text.WrapAnywhere
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: app.compactUi ? 5 : 12
                            Text { text: "识别与语音"; visible: !app.compactUi; color: "#111827"; font.pixelSize: 32; font.bold: true; font.family: app.font.family }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 76 : 128
                                radius: 6
                                color: "#EFF6FF"
                                border.color: "#93C5FD"
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: app.compactUi ? 8 : 12
                                    spacing: app.compactUi ? 2 : 4
                                    Text {
                                        text: recentScanStatus === "success" ? recentScanResult : statusMessage
                                        color: recentScanError ? "#B91C1C" : "#0F172A"
                                        font.pixelSize: app.compactUi ? 20 : 30
                                        font.bold: true
                                        font.family: app.font.family
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                    Text {
                                        text: "语音理解：" + ((state.latest_speech_parsed && state.latest_speech_parsed.canonical_command) ? state.latest_speech_parsed.canonical_command : speechIntentText()) +
                                              " / 方式：" + ((state.latest_speech_parsed && state.latest_speech_parsed.match_method) ? state.latest_speech_parsed.match_method : "-")
                                        color: "#1D4ED8"
                                        font.pixelSize: app.compactUi ? 15 : 22
                                        font.family: app.font.family
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10
                                        Text {
                                            text: visionConclusionText()
                                            color: confidenceColor(state.latest_vision_confidence)
                                            font.pixelSize: app.compactUi ? 15 : 21
                                            font.bold: true
                                            font.family: app.font.family
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }
                                        Rectangle {
                                            Layout.preferredWidth: app.compactUi ? 112 : 150
                                            Layout.preferredHeight: app.compactUi ? 26 : 34
                                            radius: 17
                                            color: "#FEF3C7"
                                            border.color: "#F59E0B"
                                            Text {
                                                anchors.centerIn: parent
                                                text: referenceScoreText(state.latest_vision_confidence)
                                                color: "#92400E"
                                                font.pixelSize: app.compactUi ? 15 : 20
                                                font.bold: true
                                                font.family: app.font.family
                                                elide: Text.ElideNone
                                            }
                                        }
                                        Text {
                                            text: visionLatencyText()
                                            color: "#475569"
                                            font.pixelSize: app.compactUi ? 14 : 19
                                            font.family: app.font.family
                                            elide: Text.ElideNone
                                        }
                                    }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 48 : 92
                                radius: 6
                                color: "#F8FAFC"
                                border.color: "#E2E8F0"
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 2
                                    Text { text: "拍照状态：" + (state.latest_capture_status || "idle") + " / " + (state.latest_capture_message || captureMessage || "-"); color: "#475569"; font.pixelSize: app.compactUi ? 13 : 17; font.family: app.font.family; Layout.fillWidth: true; elide: Text.ElideRight }
                                    Text { text: state.latest_capture ? (state.latest_capture + " / " + (state.latest_capture_latency_ms || 0) + " ms") : "暂无拍照"; color: "#0F172A"; font.pixelSize: app.compactUi ? 14 : 19; font.bold: true; font.family: app.font.family; elide: Text.ElideMiddle; Layout.fillWidth: true }
                                    Text { visible: !app.compactUi; text: "照片：" + (state.capture_count || 0) + " 张 / " + (state.capture_total_size_mb || 0) + " MB"; color: "#475569"; font.pixelSize: 16; font.family: app.font.family; Layout.fillWidth: true }
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 116 : 270
                                radius: 6
                                color: "#F8FAFC"
                                border.color: "#E2E8F0"
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: app.compactUi ? 8 : 12
                                    spacing: app.compactUi ? 2 : 4
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 10
                                        Text { text: visionReferenceText(); color: "#0F172A"; font.pixelSize: app.compactUi ? 14 : 19; font.bold: true; font.family: app.font.family; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Rectangle {
                                            Layout.preferredWidth: app.compactUi ? 112 : 150
                                            Layout.preferredHeight: app.compactUi ? 24 : 32
                                            radius: 16
                                            color: "#FEF3C7"
                                            border.color: "#F59E0B"
                                            Text { anchors.centerIn: parent; text: referenceScoreText(state.latest_vision_confidence); color: "#92400E"; font.pixelSize: app.compactUi ? 14 : 18; font.bold: true; font.family: app.font.family; elide: Text.ElideNone }
                                        }
                                        Text { text: visionLatencyText(); color: "#475569"; font.pixelSize: app.compactUi ? 13 : 17; font.family: app.font.family; elide: Text.ElideNone }
                                    }
                                    Text { text: top3Text(); color: "#2563EB"; font.pixelSize: app.compactUi ? 13 : 16; font.family: app.font.family; Layout.fillWidth: true; wrapMode: Text.WordWrap; maximumLineCount: app.compactUi ? 1 : 2; elide: Text.ElideRight }
                                    Text { text: voiceGuardEnabled ? ("语音守候：" + voiceGuardMessage) : ("语音操作：" + voiceSessionMessage); color: "#334155"; font.pixelSize: app.compactUi ? 15 : 22; font.bold: true; wrapMode: Text.WordWrap; maximumLineCount: app.compactUi ? 1 : 2; elide: Text.ElideRight; Layout.fillWidth: true; font.family: app.font.family }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text { text: "模式：" + voiceMode; color: "#0F172A"; font.pixelSize: app.compactUi ? 13 : 19; font.bold: true; font.family: app.font.family; Layout.fillWidth: true }
                                        Text { text: "识别：" + voiceRawText; color: "#2563EB"; font.pixelSize: app.compactUi ? 13 : 18; font.family: app.font.family; Layout.fillWidth: true; elide: Text.ElideRight }
                                        Text { text: "数字：" + voiceDigit; color: "#B45309"; font.pixelSize: app.compactUi ? 13 : 18; font.family: app.font.family }
                                    }
                                    Text { visible: !app.compactUi; text: voiceGuardEnabled ? "正在守候：请说“小售小售”" : voicePrompt; color: "#475569"; font.pixelSize: 20; font.bold: true; font.family: app.font.family; Layout.fillWidth: true; elide: Text.ElideRight }
                                    Text { visible: !app.compactUi; text: "音频：" + ((state.audio && state.audio.output_device) ? state.audio.output_device : "-") + " / 播报：" + ((state.audio && state.audio.latest_event) ? state.audio.latest_event : "-"); color: "#475569"; font.pixelSize: 15; elide: Text.ElideRight; Layout.fillWidth: true; font.family: app.font.family }
                                    RowLayout {
                                        visible: !app.compactUi
                                        Layout.fillWidth: true
                                        spacing: 8
                                        Button {
                                            text: voiceGuardEnabled ? "守候中" : "开启语音守候"
                                            enabled: !voiceGuardEnabled && !speechBusy
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 42
                                            font.pixelSize: 18
                                            onClicked: startVoiceGuard()
                                        }
                                        Button {
                                            text: "停止语音守候"
                                            enabled: voiceGuardEnabled
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 42
                                            font.pixelSize: 18
                                            onClicked: stopVoiceGuard()
                                        }
                                    }
                                }
                            }

                            Text {
                                visible: !app.compactUi
                                text: "语音指令请说完整短句：小售小售一号查询总价 / 小售小售四号结账；点击语音按钮后说：一号查询总价 / 四号结账"
                                color: "#0F172A"
                                font.pixelSize: 24
                                font.bold: true
                                font.family: app.font.family
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 46 : 92
                                spacing: app.compactUi ? 5 : 8
                                Repeater {
                                    model: voiceMenuCardsModel()
                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        radius: 5
                                        color: modelData.digit === "0" ? "#FEE2E2" : "#DBEAFE"
                                        border.color: "#93C5FD"
                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.recommended_phrase || (modelData.digit + "号 " + modelData.label)
                                            color: "#1E3A8A"
                                            width: parent.width - 8
                                            font.pixelSize: app.compactUi ? 13 : 23
                                            font.bold: true
                                            font.family: app.font.family
                                            wrapMode: Text.WordWrap
                                            horizontalAlignment: Text.AlignHCenter
                                        }
                                    }
                                }
                            }

                            TextField {
                                id: speechInput
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 40 : 58
                                placeholderText: "手动测试：小售小售一号查询总价 / 小售小售四号结账；点击语音按钮后说一号查询总价"
                                font.pixelSize: app.compactUi ? 15 : 22
                                font.family: app.font.family
                                onActiveFocusChanged: {
                                    inputModeText = activeFocus ? "语音编辑，条码仍优先转扫码" : "扫码优先";
                                    if (!activeFocus) ensureScannerFocus();
                                }
                                Keys.priority: Keys.BeforeItem
                                Keys.onPressed: {
                                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                        routeAcceptedInput(text, "speech_field");
                                        event.accepted = true;
                                    }
                                }
                                onAccepted: routeAcceptedInput(text, "speech_field")
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: app.compactUi ? 56 : 98
                                radius: 6
                                color: scannerCaptureInput.activeFocus ? "#ECFDF5" : "#FEF2F2"
                                border.color: scannerCaptureInput.activeFocus ? "#22C55E" : "#EF4444"
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 2
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Text { text: scannerFocusText(); color: scannerCaptureInput.activeFocus ? "#166534" : "#991B1B"; font.pixelSize: app.compactUi ? 13 : 18; font.bold: true; font.family: app.font.family; Layout.fillWidth: true }
                                        Text { text: recentScanTime; color: "#475569"; font.pixelSize: app.compactUi ? 12 : 16; font.family: app.font.family }
                                    }
                                    Text { text: "最近扫码：" + recentScanRaw; color: "#0F172A"; font.pixelSize: app.compactUi ? 12 : 17; font.family: app.font.family; elide: Text.ElideRight; Layout.fillWidth: true }
                                    Text { text: "结果：" + recentScanStatus + " / " + recentScanResult; color: recentScanError ? "#B91C1C" : "#2563EB"; font.pixelSize: app.compactUi ? 12 : 17; font.family: app.font.family; elide: Text.ElideRight; Layout.fillWidth: true }
                                    Text { visible: !app.compactUi; text: "模式：" + inputModeText + " / 路由：" + recentRoute + " / 语音：" + recentSpeechCommand; color: "#475569"; font.pixelSize: 15; font.family: app.font.family; elide: Text.ElideRight; Layout.fillWidth: true }
                                }
                            }
                        }
                    }
                }

                ProductPanel {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    productsModel: quickProductModel
                    onAddProduct: {
                        busy = true;
                        statusMessage = "正在加入：" + productName;
                        RetailApi.addProduct(productId, function(ok, data) {
                            busy = false;
                            setResult(ok, data, ok ? ("已加入：" + productName) : "加购失败");
                        });
                    }
                }
            }

            CartPanel {
                Layout.fillHeight: true
                Layout.preferredWidth: app.cartPanelWidth
                Layout.minimumWidth: app.compactUi ? 560 : 650
                Layout.maximumWidth: app.compactUi ? 760 : 860
                compact: app.compactUi
                cart: cartForPanel()
                cartItemsModel: cartItemModel
                onRemoveProduct: {
                    busy = true;
                    statusMessage = "正在删除商品：" + productId;
                    RetailApi.removeProduct(productId, function(ok, data) {
                        busy = false;
                        setResult(ok, data, ok ? "商品已删除" : "删除失败");
                    });
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: app.scanBarHeight
            color: "#F8FAFC"
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: app.compactUi ? 14 : 22
                anchors.rightMargin: app.compactUi ? 14 : 22
                spacing: app.compactUi ? 10 : 16
                TextField {
                    id: scanInput
                    Layout.fillWidth: true
                    Layout.preferredHeight: app.compactUi ? 52 : 68
                    placeholderText: "扫码或输入 SKU，例如 SKU006 / 690000000006"
                    font.pixelSize: app.compactUi ? 18 : 25
                    font.family: app.font.family
                    onAccepted: doScan()
                    onActiveFocusChanged: { if (!activeFocus) ensureScannerFocus(); }
                }
            }
        }

        ActionButtons {
            Layout.fillWidth: true
            Layout.preferredHeight: app.actionBarHeight
            compact: app.compactUi
            busy: app.busy
            captureBusy: app.captureBusy
            speechBusy: app.speechBusy
            onRefresh: {
                statusMessage = "正在刷新";
                refreshNow();
                ensureScannerFocus();
            }
            onCapture: {
                if (captureBusy) {
                    captureMessage = "拍照中，请稍后";
                    statusMessage = "拍照中，请稍后";
                    ensureScannerFocus();
                    return;
                }
                captureBusy = true;
                captureMessage = "拍照中...";
                statusMessage = "正在拍照";
                RetailApi.capture(function(ok, data) {
                    captureBusy = false;
                    captureMessage = ok ? (data.message || ("拍照成功：" + (data.image_path || ""))) : ("拍照失败：" + ((data && (data.message || data.error)) || "未知错误"));
                    if (ok) {
                        updateCapturePreview(data);
                        statusMessage = "拍照成功，正在自动识别";
                        runVisionPredict(data.image_path || capturePreviewPath);
                    } else {
                        setResult(false, data, "拍照失败");
                    }
                    ensureScannerFocus();
                });
            }
            onSpeech: {
                startVoiceSession();
            }
            onRemoveLast: {
                busy = true;
                statusMessage = "正在删除上一件";
                RetailApi.removeLast(function(ok, data) {
                    busy = false;
                    setResult(ok, data, ok ? "已删除上一件" : "购物车为空");
                    ensureScannerFocus();
                });
            }
            onClearCart: doClearCart()
            onCheckout: doCheckout()
        }

        StatusBar {
            Layout.fillWidth: true
            Layout.preferredHeight: app.statusBarHeight
            compact: app.compactUi
            online: app.online
            paymentStatus: paymentStatusText()
            audioStatus: state.audio ? state.audio.output_device : ""
            message: statusMessage
        }
    }

    PaymentDialog {
        id: paymentDialog
        onPaidConfirmed: {
            statusMessage = "支付成功，已返回收银台：" + (order.order_id || "");
            refreshNow();
        }
    }

    Dialog {
        id: confirmDialog
        property string actionName: ""
        property string message: ""
        modal: true
        focus: true
        title: "确认操作"
        standardButtons: Dialog.NoButton
        width: 520
        height: 260
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 22
            spacing: 20
            Text {
                text: confirmDialog.message
                font.pixelSize: 24
                font.family: app.font.family
                color: "#111827"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            RowLayout {
                Layout.fillWidth: true
                Button {
                    text: "取消"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 58
                    font.pixelSize: 22
                    onClicked: { confirmDialog.close(); ensureScannerFocus(); }
                }
                Button {
                    text: "确认"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 58
                    font.pixelSize: 22
                    onClicked: executeConfirmedAction()
                }
            }
        }
    }
}
