import React, { useState, useRef } from 'react';
import { Card } from '@/components/ui/button';
import { Bold, Italic, Underline, List, ListOrdered } from 'lucide-react';

const RichTextEditor = ({ label, value, onChange, enabled, onToggle }) => {
  const editorRef = useRef(null);

  const execCommand = (command, value = null) => {
    document.execCommand(command, false, value);
    if (editorRef.current) {
      onChange(editorRef.current.innerHTML);
    }
  };

  const handleInput = (e) => {
    onChange(e.target.innerHTML);
  };

  return (
    <div className="border rounded-lg p-4 bg-white">
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-semibold text-gray-700">{label}</label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={enabled}
            onChange={onToggle}
            className="w-4 h-4 text-rose-600 border-gray-300 rounded focus:ring-rose-500"
          />
          <span className="text-sm text-gray-600">Enable this section</span>
        </label>
      </div>

      {enabled && (
        <>
          <div className="flex gap-1 mb-2 p-2 bg-gray-50 rounded border">
            <button
              type="button"
              onClick={() => execCommand('bold')}
              className="p-2 hover:bg-gray-200 rounded"
              title="Bold"
            >
              <Bold className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => execCommand('italic')}
              className="p-2 hover:bg-gray-200 rounded"
              title="Italic"
            >
              <Italic className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => execCommand('underline')}
              className="p-2 hover:bg-gray-200 rounded"
              title="Underline"
            >
              <Underline className="w-4 h-4" />
            </button>
            <div className="w-px bg-gray-300 mx-1" />
            <button
              type="button"
              onClick={() => execCommand('insertUnorderedList')}
              className="p-2 hover:bg-gray-200 rounded"
              title="Bullet List"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => execCommand('insertOrderedList')}
              className="p-2 hover:bg-gray-200 rounded"
              title="Numbered List"
            >
              <ListOrdered className="w-4 h-4" />
            </button>
          </div>

          <div
            ref={editorRef}
            contentEditable
            onInput={handleInput}
            dangerouslySetInnerHTML={{ __html: value || '' }}
            className="min-h-[150px] p-3 border rounded bg-white focus:outline-none focus:ring-2 focus:ring-rose-500"
            style={{
              maxHeight: '300px',
              overflowY: 'auto'
            }}
          />
          <p className="text-xs text-gray-500 mt-1">
            Use the toolbar above to format your text
          </p>
        </>
      )}

      {!enabled && (
        <p className="text-sm text-gray-500 italic">
          This section is currently disabled. Enable it to add content.
        </p>
      )}
    </div>
  );
};

export default RichTextEditor;
