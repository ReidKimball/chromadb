'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, TextField, Button, Typography, Select, MenuItem, FormControl, InputLabel, CircularProgress, Card, CardContent, Divider } from '@mui/material';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// Define types for our state
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ParsedAnalysis {
    used_sentences: string;
    reasoning: string;
    confidence: string;
}

// Helper function to parse the AI analysis string
const parseAnalysis = (analysisText: string): ParsedAnalysis => {
    const usedSentencesMatch = analysisText.match(/1\.\s*\*\*Sentences used:\*\*\s*([\s\S]*?)(?=2\.\s*\*\*Reasoning:\*\*|$)/);
    const reasoningMatch = analysisText.match(/2\.\s*\*\*Reasoning:\*\*\s*([\s\S]*?)(?=3\.\s*\*\*Confidence Level:\*\*|$)/);
    const confidenceMatch = analysisText.match(/3\.\s*\*\*Confidence Level:\*\*\s*([\s\S]*)/);

    // Helper to clean up the captured text by removing leading asterisks and trimming whitespace
    const cleanText = (text: string | undefined | null): string => {
        if (!text) return 'Not available.';
        return text.replace(/\*/g, '').trim();
    };

    return {
        used_sentences: cleanText(usedSentencesMatch?.[1]),
        reasoning: cleanText(reasoningMatch?.[1]),
        confidence: cleanText(confidenceMatch?.[1]),
    };
};


export default function ChatPage() {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [diet, setDiet] = useState('SCD'); // Default diet
  const [analysis, setAnalysis] = useState<ParsedAnalysis | null>(null);
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
    setAnalysis(null); // Clear previous analysis

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_prompt: "You are a helpful and friendly AI assistant specializing in dietary information. Your name is Nutri-Chat. You must answer user questions based *only* on the context provided. After your user-facing reply, you MUST include a special <AI_ANALYSIS> block. In this block, you will 'think out loud'. First, state which specific sentences from the context you used to form your answer. Second, explain your reasoning step-by-step. Third, state your confidence level (High, Medium, or Low). If the context does not contain the answer, you must state that and explain why the provided context is insufficient.",
          system_prompt_filename: 'default.md',
          diet: diet,
          history: messages,
          user_message: input,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage: Message = { role: 'assistant', content: data.reply };
      setMessages(prev => [...prev, assistantMessage]);
      if (data.analysis) {
        setAnalysis(parseAnalysis(data.analysis));
      }

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
    if (typeof window !== 'undefined') {
        const rawMarkup = marked(content);
        const sanitizedMarkup = DOMPurify.sanitize(rawMarkup as string);
        return { __html: sanitizedMarkup };
    }
    return { __html: '' };
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', p: 2, backgroundColor: '#f5f5f5' }}>

      {/* AI Analysis Column */}
      <Box sx={{ width: '40%', pr: 2, display: 'flex', flexDirection: 'column' }}>
        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', borderRadius: '12px' }}>
          <CardContent sx={{ flexGrow: 1, overflowY: 'auto' }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: 'text.primary' }}>
              AI Analysis
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {analysis ? (
              <>
                <Typography variant="h6" gutterBottom>Confidence</Typography>
                <Typography paragraph sx={{ fontWeight: 'bold', color: analysis.confidence === 'High' ? 'green' : 'orange' }}>
                  {analysis.confidence}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Reasoning</Typography>
                <Typography paragraph>{analysis.reasoning}</Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Sources Used</Typography>
                <Typography paragraph sx={{ fontStyle: 'italic', color: 'text.secondary' }}>{analysis.used_sentences}</Typography>
              </>
            ) : (
              <Typography sx={{ color: 'text.secondary' }}>
                {isLoading ? 'Generating analysis...' : 'Analysis will appear here after you send a message.'}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* User Chat Column */}
      <Box sx={{ width: '60%', display: 'flex', flexDirection: 'column' }}>
        <Paper sx={{ flexGrow: 1, p: 2, display: 'flex', flexDirection: 'column', overflow: 'hidden', mb: 2, backgroundColor: 'white', borderRadius: '12px' }}>
            <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 1 }}>
                {messages.length === 0 && !isLoading && (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%'}}>
                        <Typography variant="h6" sx={{color: 'text.secondary'}}>Start a conversation with Nutri-Chat!</Typography>
                    </Box>
                )}
                {messages.map((msg, index) => (
                  <Box key={index} sx={{ mb: 2, display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                    <Box sx={{
                        p: 1.5,
                        display: 'inline-block',
                        maxWidth: '80%',
                        backgroundColor: msg.role === 'user' ? 'primary.main' : 'grey.200',
                        color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                        borderRadius: msg.role === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
                        boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
                      }}
                    >
                      <div dangerouslySetInnerHTML={renderMarkdown(msg.content)} />
                    </Box>
                  </Box>
                ))}
                {isLoading && !analysis && ( // Show loading indicator in chat only before response arrives
                  <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                     <CircularProgress size={24} />
                  </Box>
                )}
                <div ref={chatEndRef} />
            </Box>
        </Paper>

        {/* Input Area */}
        <Box sx={{ display: 'flex', gap: 1.5, flexShrink: 0 }}>
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
          <FormControl variant="outlined" size="medium" sx={{ minWidth: 120, backgroundColor: 'white', borderRadius: '8px' }}>
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
            sx={{ borderRadius: '8px', px: 4, py: '15px' }}
          >
            Send
          </Button>
        </Box>
      </Box>

    </Box>
  );
}
