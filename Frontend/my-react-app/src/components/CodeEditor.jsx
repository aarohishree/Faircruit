import React, { useState } from 'react';

const CodeEditor = ({ initialCode, onChange, value }) => {
  const [language, setLanguage] = useState('python');

  return (
    <div className="code-editor">
      <div className="editor-header">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="language-select"
        >
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
          <option value="sql">SQL</option>
        </select>
      </div>

      <textarea
        className="code-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck="false"
        style={{ fontFamily: "'Courier New', monospace" }}
      />

      <style>{`
        .code-editor {
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          overflow: hidden;
          background: #2d3748;
        }

        .editor-header {
          background: #1a202c;
          padding: 12px;
          border-bottom: 1px solid #4a5568;
        }

        .language-select {
          padding: 6px 12px;
          background: #2d3748;
          color: #e2e8f0;
          border: 1px solid #4a5568;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
        }

        .code-input {
          width: 100%;
          height: 300px;
          padding: 16px;
          background: #2d3748;
          color: #e2e8f0;
          border: none;
          font-family: 'Courier New', monospace;
          font-size: 0.95rem;
          line-height: 1.6;
          resize: vertical;
          outline: none;
        }

        .code-input:focus {
          background: #323c47;
        }
      `}</style>
    </div>
  );
};

export default CodeEditor;
