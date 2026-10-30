import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface StreamingTextProps {
  content: string;
  speed?: number; // chars per tick
  tickInterval?: number; // ms per tick
  isMarkdown?: boolean;
  className?: string;
  onComplete?: () => void;
}

export const StreamingText: React.FC<StreamingTextProps> = ({
  content = '',
  speed = 18,
  tickInterval = 25,
  isMarkdown = true,
  className = '',
  onComplete,
}) => {
  const [displayedText, setDisplayedText] = useState<string>('');
  const [isDone, setIsDone] = useState<boolean>(false);
  const indexRef = useRef<number>(0);

  useEffect(() => {
    if (!content) {
      setDisplayedText('');
      setIsDone(true);
      return;
    }

    // If text is short (< 50 chars), render immediately
    if (content.length < 50) {
      setDisplayedText(content);
      setIsDone(true);
      if (onComplete) onComplete();
      return;
    }

    indexRef.current = 0;
    setDisplayedText('');
    setIsDone(false);

    const interval = setInterval(() => {
      indexRef.current = Math.min(indexRef.current + speed, content.length);
      setDisplayedText(content.slice(0, indexRef.current));

      if (indexRef.current >= content.length) {
        clearInterval(interval);
        setIsDone(true);
        if (onComplete) onComplete();
      }
    }, tickInterval);

    return () => clearInterval(interval);
  }, [content, speed, tickInterval, onComplete]);

  return (
    <div className={`relative ${className}`}>
      {isMarkdown ? (
        <ReactMarkdown>{displayedText}</ReactMarkdown>
      ) : (
        <span>{displayedText}</span>
      )}
      {!isDone && (
        <span className="inline-block w-1.5 h-3.5 bg-accent ml-1 animate-pulse align-middle" />
      )}
    </div>
  );
};

export default StreamingText;
