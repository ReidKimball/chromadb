'use client';

import { useState, useRef, useEffect } from 'react';
import { Box, Grid, Paper, TextField, Button, Typography, Select, MenuItem, FormControl, InputLabel, CircularProgress } from '@mui/material';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Define types for our state
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Analysis {
  used_sentences: string;
  reasoning: string;
  confidence: string;
}

export default function Home() {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [diet, setDiet] = useState('SCD'); // Default diet
  const [analysis, setAnalysis] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const chatEndRef = useRef<null | HTMLDivElement>(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_prompt: "You are a helpful and friendly AI assistant specializing in dietary information. Your name is Nutri-Chat. You must answer user questions based *only* on the context provided. After your user-facing reply, you MUST include a special <AI_ANALYSIS> block. In this block, you will 'think out loud'. First, state which specific sentences from the context you used to form your answer. Second, explain your reasoning step-by-step. Third, state your confidence level (High, Medium, or Low). If the context does not contain the answer, you must state that and explain why the provided context is insufficient.",
          system_prompt_filename: 'default.md',
          diet: diet,
          history: messages, // Send previous messages for context
          user_message: input,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage: Message = { role: 'assistant', content: data.reply };
      setMessages(prev => [...prev, assistantMessage]);
      setAnalysis(data.analysis);

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Sanitize and render markdown content
  const renderMarkdown = (content: string) => {
    const rawMarkup = marked(content);
    const sanitizedMarkup = DOMPurify.sanitize(rawMarkup as string);
    return { __html: sanitizedMarkup };
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', backgroundColor: 'grey.50' }}>
      <Grid container sx={{ flexGrow: 1 }}>
        {/* Left Column: AI Analysis */}
        <Grid item xs={12} md={5} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100vh' }}>
          <Typography variant="h5" gutterBottom sx={{ flexShrink: 0 }}>AI Analysis</Typography>
          <Paper elevation={3} sx={{ flexGrow: 1, p: 2, overflowY: 'auto', whiteSpace: 'pre-wrap', backgroundColor: '#f5f5f5' }}>
            {analysis || 'The AI\'s reasoning and context will appear here.'}
          </Paper>
        </Grid>

        {/* Right Column: Chat Interface */}
        <Grid item xs={12} md={7} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100vh' }}>
          <Typography variant="h5" gutterBottom sx={{ flexShrink: 0 }}>Chat</Typography>
          <Paper elevation={3} sx={{ flexGrow: 1, p: 2, overflowY: 'auto', mb: 2, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flexGrow: 1 }}>
              {messages.map((msg, index) => (
                <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <Paper 
                    elevation={1} 
                    sx={{
                      p: 1.5, 
                      display: 'inline-block', 
                      maxWidth: '80%',
                      backgroundColor: msg.role === 'user' ? '#d1e7fd' : '#e9ecef',
                    }}
                  >
                    <div dangerouslySetInnerHTML={renderMarkdown(msg.content)} />
                  </Paper>
                </Box>
              ))}
              {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                   <CircularProgress size={24} />
                </Box>
              )}
              <div ref={chatEndRef} />
            </Box>
          </Paper>
          
          {/* Input Area */}
          <Box sx={{ display: 'flex', gap: 2, flexShrink: 0 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
              disabled={isLoading}
            />
            <FormControl variant="outlined" sx={{ minWidth: 120 }}>
              <InputLabel>Diet</InputLabel>
              <Select
                value={diet}
                onChange={(e) => setDiet(e.target.value)}
                label="Diet"
                disabled={isLoading}
              >
                <MenuItem value="SCD">SCD</MenuItem>
                <MenuItem value="GAPS">GAPS</MenuItem>
                <MenuItem value="Paleo AIP">Paleo AIP</MenuItem>
                <MenuItem value="Mediterranean">Mediterranean</MenuItem>
              </Select>
            </FormControl>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleSendMessage} 
              disabled={isLoading}
            >
              Send
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
