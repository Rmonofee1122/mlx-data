<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>裏垢女子チャット</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; background: #f8f8f8; }
    #chat { max-width: 700px; margin: auto; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 0 10px #ccc; }
    .msg { margin: 0.5rem 0; }
    .user { text-align: right; color: #007bff; }
    .bot { text-align: left; color: #e91e63; }
    .error { text-align: left; color: #ff0000; }
    .variant { padding-left: 1rem; margin-top: 0.3rem; font-size: 0.95rem; }
    input, button, select { padding: 0.5rem; font-size: 1rem; margin-right: 0.5rem; }
    .controls { margin-top: 1rem; }
    textarea { width: 100%; height: 150px; margin-top: 1rem; font-family: monospace; white-space: pre; }
    
    /* プログレスバー関連のスタイル */
    #progressContainer {
      display: none;
      margin: 1rem 0;
      width: 100%;
    }
    #progressBar {
      width: 0%;
      height: 10px;
      background-color: #e91e63;
      border-radius: 5px;
      transition: width 0.3s ease;
      animation: pulse 1.5s infinite;
    }
    #progressStatus {
      font-size: 0.9rem;
      color: #666;
      margin-top: 0.3rem;
      text-align: center;
    }
    @keyframes pulse {
      0% { opacity: 0.6; }
      50% { opacity: 1; }
      100% { opacity: 0.6; }
    }
  </style>
</head>
<body>
  <div id="chat">
    <h2>裏垢女子キャプション・チャット</h2>
    <div id="messages"></div>

    <input id="prompt" placeholder="プロンプトを入力..." size="50"><br>

    <!-- プログレスバー -->
    <div id="progressContainer">
      <div id="progressBar"></div>
      <div id="progressStatus">生成中...</div>
    </div>

    <div class="controls">
      🔁 複数案: <input type="number" id="num" value="3" min="1" max="10">
      <label><input type="checkbox" id="jsonMode"> JSON形式で出力</label>
      <button id="sendButton">送信</button>
    </div>

    <div id="jsonOutput" style="display:none;">
      <h4>📦 JSON出力</h4>
      <textarea id="jsonArea" readonly></textarea>
    </div>
  </div>

  <script>
    // DOM要素の参照を取得
    const promptInput = document.getElementById("prompt");
    const numInput = document.getElementById("num");
    const jsonModeCheckbox = document.getElementById("jsonMode");
    const sendButton = document.getElementById("sendButton");
    const messagesContainer = document.getElementById("messages");
    const progressContainer = document.getElementById("progressContainer");
    const progressBar = document.getElementById("progressBar");
    const jsonOutput = document.getElementById("jsonOutput");
    const jsonArea = document.getElementById("jsonArea");

    // プログレスバーのアニメーション用変数
    let progressInterval = null;

    // 送信ボタンのイベントリスナー
    sendButton.addEventListener("click", send);

    // Enterキーでも送信できるようにする
    promptInput.addEventListener("keypress", function(event) {
      if (event.key === "Enter") {
        send();
      }
    });

    // JSON表示モードの切り替え
    jsonModeCheckbox.addEventListener("change", function() {
      jsonOutput.style.display = this.checked ? "block" : "none";
    });

    // メッセージ送信処理
    async function send() {
      const prompt = promptInput.value.trim();
      const num = parseInt(numInput.value);
      const jsonMode = jsonModeCheckbox.checked;

      if (!prompt) return;

      // 送信ボタンを無効化
      sendButton.disabled = true;
      
      // プログレスバーを表示
      progressContainer.style.display = "block";
      
      // プログレスバーのアニメーション開始
      startProgressAnimation();

      // ユーザーメッセージを表示
      addMessage("user", prompt);

      try {
        const res = await fetch("/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: prompt,
            max_tokens: 300,
            num_return_sequences: num,
          })
        });

        const data = await res.json();

        // 生成完了時にプログレスバーを100%にする
        completeProgress();

        if (Array.isArray(data.responses)) {
          if (jsonMode) {
            // JSON形式で表示
            jsonOutput.style.display = "block";
            jsonArea.value = JSON.stringify(
              data.responses.map(text => ({ response: text })),
              null,
              2
            );
          } else {
            // 通常チャット形式で表示
            jsonOutput.style.display = "none";
            data.responses.forEach((text, index) => {
              addBotMessage(text, index + 1);
            });
          }
        } else {
          addErrorMessage(`取得失敗: ${data.response || "形式不正"}`);
        }
      } catch (error) {
        // エラー発生時
        stopProgress();
        addErrorMessage(`エラーが発生しました: ${error.message}`);
      }

      // 入力をクリア
      promptInput.value = "";
    }

    // ユーザーメッセージを追加
    function addMessage(type, content) {
      const msgDiv = document.createElement("div");
      msgDiv.className = `msg ${type}`;
      
      if (type === "user") {
        msgDiv.innerHTML = `🧑‍💻 ${content}`;
      }
      
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    }

    // ボットのメッセージを追加
    function addBotMessage(content, variantNum) {
      const msgDiv = document.createElement("div");
      msgDiv.className = "msg bot";
      msgDiv.innerHTML = `💋 <span class="variant">案 ${variantNum}: ${content}</span>`;
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    }

    // エラーメッセージを追加
    function addErrorMessage(content) {
      const msgDiv = document.createElement("div");
      msgDiv.className = "msg error";
      msgDiv.innerHTML = `⚠️ ${content}`;
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    }

    // 最下部にスクロール
    function scrollToBottom() {
      window.scrollTo(0, document.body.scrollHeight);
    }

    // プログレスバーのアニメーション開始
    function startProgressAnimation() {
      let progress = 0;
      progressInterval = setInterval(() => {
        // 進捗を徐々に増加（最大95%まで）
        if (progress < 95) {
          progress += Math.random() * 5;
          if (progress > 95) progress = 95;
          progressBar.style.width = `${progress}%`;
        }
      }, 300);
    }

    // プログレスバーを完了状態にする
    function completeProgress() {
      clearInterval(progressInterval);
      progressBar.style.width = "100%";
      
      // 少し待ってからプログレスバーを非表示にする
      setTimeout(() => {
        progressContainer.style.display = "none";
        progressBar.style.width = "0%";
        sendButton.disabled = false;
      }, 500);
    }

    // プログレスバーを停止
    function stopProgress() {
      clearInterval(progressInterval);
      progressContainer.style.display = "none";
      progressBar.style.width = "0%";
      sendButton.disabled = false;
    }
  </script>
</body>
</html>