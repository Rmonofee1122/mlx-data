// @ts-nocheck
/*
 * このファイルはReactコンポーネントとして実装されています。
 * 実行するには以下のパッケージが必要です：
 * - react
 * - react-dom
 * - typescript
 *
 * インストール方法:
 * npm install react react-dom typescript @types/react @types/react-dom
 * または
 * yarn add react react-dom typescript @types/react @types/react-dom
 */

import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import './styles/global.css';

interface SystemInfo {
  cpu: number;
  memory: number;
}

interface GenerateResponse {
  responses?: string[];
  response?: string;
}

const Chat: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'bot', content: string }>>([]);
  const [numResponses, setNumResponses] = useState<number>(3);
  const [jsonMode, setJsonMode] = useState<boolean>(false);
  const [jsonOutput, setJsonOutput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [systemInfo, setSystemInfo] = useState<SystemInfo>({ cpu: 0, memory: 0 });

  // システム情報を取得する関数
  const updateSystemInfo = async () => {
    try {
      const response = await fetch("/system-info");
      const data: SystemInfo = await response.json();
      setSystemInfo(data);
    } catch (error) {
      console.error("システム情報の取得に失敗しました:", error);
    }
  };

  // 定期的にシステム情報を更新
  useEffect(() => {
    // ページ読み込み時に初回実行
    updateSystemInfo();
    
    // 3秒ごとに更新
    const interval = setInterval(updateSystemInfo, 3000);
    
    // クリーンアップ関数
    return () => clearInterval(interval);
  }, []);

  // 送信処理
  const handleSend = async () => {
    if (!prompt) return;

    // 送信前の状態設定
    setIsLoading(true);
    setProgress(0);
    
    // メッセージリストに追加
    setMessages(prev => [...prev, { type: 'user', content: prompt }]);

    // プログレスバーのアニメーション
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev < 95) {
          const newProgress = prev + Math.random() * 5;
          return newProgress > 95 ? 95 : newProgress;
        }
        return prev;
      });
    }, 300);

    try {
      const res = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt,
          max_tokens: 300,
          num_return_sequences: numResponses,
        })
      });

      const data: GenerateResponse = await res.json();

      // 生成完了時にプログレスバーを100%にする
      clearInterval(progressInterval);
      setProgress(100);
      
      // 少し待ってからプログレスバーをリセット
      setTimeout(() => {
        setIsLoading(false);
        setProgress(0);
      }, 500);

      if (Array.isArray(data.responses)) {
        if (jsonMode) {
          // JSON形式で表示
          setJsonOutput(JSON.stringify(
            data.responses.map(text => ({ response: text })),
            null,
            2
          ));
        } else {
          // 通常チャット形式で表示
          data.responses.forEach((text, index) => {
            setMessages(prev => [...prev, { 
              type: 'bot', 
              content: `💋 <span class="variant">案 ${index + 1}: ${text}</span>` 
            }]);
          });
        }
      } else {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: `⚠️ 取得失敗: ${data.response || "形式不正"}` 
        }]);
      }
    } catch (error: any) {
      // エラー発生時
      clearInterval(progressInterval);
      setIsLoading(false);
      setProgress(0);
      
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: `⚠️ エラーが発生しました: ${error.message}` 
      }]);
    }

    // 入力欄をクリア
    setPrompt('');
  };

  return (
    <div>
      <div id="chat">
        <h2>裏垢女子キャプション・チャット</h2>
        <div id="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`msg ${msg.type}`} dangerouslySetInnerHTML={{ __html: msg.type === 'user' ? `🧑‍💻 ${msg.content}` : msg.content }} />
          ))}
        </div>

        <input 
          id="prompt" 
          placeholder="プロンプトを入力..." 
          size={50} 
          value={prompt}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setPrompt(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <br />

        {/* プログレスバー */}
        <div id="progressContainer" style={{ display: isLoading ? 'block' : 'none' }}>
          <div id="progressBar" style={{ width: `${progress}%` }}></div>
          <div id="progressStatus">生成中...</div>
        </div>

        <div className="controls">
          🔁 複数案: 
          <input 
            type="number" 
            id="num" 
            value={numResponses} 
            min={1} 
            max={10}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setNumResponses(parseInt(e.target.value))}
          />
          <label>
            <input 
              type="checkbox" 
              id="jsonMode" 
              checked={jsonMode}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setJsonMode(e.target.checked)}
            /> 
            JSON形式で出力
          </label>
          <button 
            id="sendButton" 
            onClick={handleSend}
            disabled={isLoading}
          >
            送信
          </button>
        </div>

        <div id="jsonOutput" style={{ display: jsonMode ? 'block' : 'none' }}>
          <h4>📦 JSON出力</h4>
          <textarea id="jsonArea" readOnly value={jsonOutput}></textarea>
        </div>
      </div>

      {/* システムモニター */}
      <div id="systemMonitor">
        <h4>システムリソース</h4>
        <div className="resource-container">
          <div className="resource">
            <span>CPU使用率:</span>
            <div className="meter">
              <div 
                id="cpuUsage" 
                className="meter-fill" 
                style={{ width: `${systemInfo.cpu}%` }}
              ></div>
            </div>
            <span id="cpuValue">{systemInfo.cpu.toFixed(1)}%</span>
          </div>
          <div className="resource">
            <span>メモリ使用率:</span>
            <div className="meter">
              <div 
                id="ramUsage" 
                className="meter-fill" 
                style={{ width: `${systemInfo.memory}%` }}
              ></div>
            </div>
            <span id="ramValue">{systemInfo.memory.toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;