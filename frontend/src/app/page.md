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
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2, backgroundColor: '#f0f2f5' }}>
        <Grid container spacing={2} sx={{ flexGrow: 1, height: '100%' }}>
          {/* Left Column: AI Analysis */}
          <Grid item xs={12} md={6} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ flexShrink: 0, color: 'text.secondary' }}>
              AI Analysis
            </Typography>
            <Paper 
              elevation={2} 
              sx={{ 
                flexGrow: 1, 
                p: 2, 
                overflowY: 'auto', 
                whiteSpace: 'pre-wrap', 
                backgroundColor: 'white', 
                borderRadius: '12px',
                height: 'calc(100% - 40px)'
              }}
            >
              {analysis ? (
                <div dangerouslySetInnerHTML={renderMarkdown(analysis)} />
              ) : (
                <Typography sx={{ color: 'text.secondary' }}>
                  The AI's reasoning and context will appear here.
                </Typography>
              )}
            </Paper>
          </Grid>

          {/* Right Column: Chat Interface */}
          <Grid item xs={12} md={6} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Typography variant="h6" gutterBottom sx={{ flexShrink: 0, color: 'text.secondary' }}>
              Chat
            </Typography>
            <Paper 
              elevation={2} 
              sx={{ 
                flexGrow: 1, 
                p: 2, 
                overflowY: 'auto', 
                mb: 2, 
                display: 'flex', 
                flexDirection: 'column', 
                backgroundColor: 'white', 
                borderRadius: '12px',
                height: 'calc(100% - 120px)'
              }}
            >
              <Box sx={{ flexGrow: 1 }}>
                {messages.map((msg, index) => (
                  <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                    <Paper 
                      elevation={0} 
                      sx={{
                        p: 1.5, 
                        display: 'inline-block', 
                        maxWidth: '80%',
                        backgroundColor: msg.role === 'user' ? 'primary.main' : 'grey.200',
                        color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                        borderRadius: '16px',
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
            <Box sx={{ flexShrink: 0 }}>
              {/* Diet Selector moved above the input box */}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                <FormControl variant="outlined" size="small" sx={{ minWidth: 180, backgroundColor: 'white', borderRadius: '8px' }}>
                  <InputLabel>Diet</InputLabel>
                  <Select
                    value={diet}
                    onChange={(e) => setDiet(e.target.value)}
                    label="Diet"
                    disabled={isLoading}
                    MenuProps={{
                      anchorOrigin: {
                        vertical: 'top',
                        horizontal: 'left',
                      },
                      transformOrigin: {
                        vertical: 'bottom',
                        horizontal: 'left',
                      },
                    }}
                  >
                    <MenuItem value="SCD">SCD</MenuItem>
                    <MenuItem value="GAPS">GAPS</MenuItem>
                    <MenuItem value="Paleo AIP">Paleo AIP</MenuItem>
                    <MenuItem value="Mediterranean">Mediterranean</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              {/* Chat Input */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Type your message..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                  disabled={isLoading}
                  sx={{ backgroundColor: 'white', borderRadius: '8px' }}
                />
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={handleSendMessage} 
                  disabled={isLoading}
                  sx={{ borderRadius: '8px', px: 4 }}
                >
                  Send
                </Button>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}
