import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

const MessageContainer = ({ message }) => {
  if (!message) return null;

  const isSuccess = message.type === 'success';
  const Icon = isSuccess ? CheckCircle : AlertCircle;

  return (
    <div className={`message ${message.type}`}>
      <Icon size={20} />
      <span>{message.text}</span>
    </div>
  );
};

export default MessageContainer;
