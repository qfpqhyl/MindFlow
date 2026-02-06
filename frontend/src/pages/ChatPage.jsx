import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  IconButton,
  Chip,
  Divider,
  Avatar,
  Card,
  CardActions,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  Skeleton,
} from '@mui/material';
import {
  Send,
  ArrowBack,
  MoreVert,
  Edit,
  Delete,
  Description,
  TaskAlt,
} from '@mui/icons-material';
import { conversationsAPI, messagesAPI, organizeAPI } from '../services/api';
import MarkdownRenderer from '../components/MarkdownRenderer';

const ChatPage = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const messagesEndRef = useRef(null);
  const streamingMessageRef = useRef(null);

  useEffect(() => {
    fetchConversation();
    fetchMessages();
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    streamingMessageRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversation = async () => {
    try {
      const response = await conversationsAPI.getDetail(conversationId);
      setConversation(response.data.data);
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await messagesAPI.getList(conversationId);
      setMessages(response.data.data.items);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    setSending(true);
    const messageContent = newMessage;
    setNewMessage('');
    setStreamingContent('');

    // Generate temporary ID for user message
    const tempUserMsgId = `temp-${Date.now()}`;

    try {
      // Add user message immediately with temporary ID
      const userMsg = {
        message_id: tempUserMsgId,
        role: 'user',
        content: messageContent,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Stream AI response
      let assistantContent = '';
      await messagesAPI.sendStream(
        conversationId,
        messageContent,
        // onChunk - called for each chunk of content
        (chunk) => {
          assistantContent += chunk;
          setStreamingContent(assistantContent);
        },
        // onComplete - called when streaming is done
        (completeData) => {
          // Add the complete assistant message to the list
          const assistantMsg = {
            message_id: completeData.message_id || Date.now().toString(),
            role: 'assistant',
            content: assistantContent,
            created_at: completeData.created_at || new Date().toISOString(),
          };
          setMessages((prev) => {
            // Remove streaming content and add assistant message
            return [...prev, assistantMsg];
          });
          setStreamingContent('');
          setSending(false);
        },
        // onError - called on error
        (error) => {
          console.error('Stream error:', error);
          setSnackbar({
            open: true,
            message: '发送失败，请重试',
            severity: 'error',
          });
          setMessages((prev) => [...prev, {
            message_id: Date.now().toString(),
            role: 'assistant',
            content: error,
            created_at: new Date().toISOString(),
          }]);
          setStreamingContent('');
          setSending(false);
        }
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      setSnackbar({
        open: true,
        message: '发送失败，请重试',
        severity: 'error',
      });
      setNewMessage(messageContent);
      setSending(false);
      setStreamingContent('');
      // Remove the temporary user message on error
      setMessages((prev) => prev.filter(msg => msg.message_id !== tempUserMsgId));
    }
  };

  const handleOrganize = async () => {
    try {
      const response = await organizeAPI.toDocument({
        conversation_id: conversationId,
        title: conversation?.title || '未命名对话',
        create_task: false,
      });

      setSnackbar({
        open: true,
        message: `已创建文档：${response.data.data.document_id.slice(0, 8)}...`,
        severity: 'success',
      });
      handleCloseMenu();
    } catch (error) {
      console.error('Failed to organize:', error);
      setSnackbar({
        open: true,
        message: '整理失败，请重试',
        severity: 'error',
      });
    }
  };

  const handleDelete = async () => {
    if (window.confirm('确定要删除这个对话吗？')) {
      try {
        await conversationsAPI.delete(conversationId);
        navigate('/conversations');
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
      handleCloseMenu();
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ pt: 4 }}>
          <Skeleton variant="rectangular" height={60} />
          <Skeleton variant="rectangular" height={200} sx={{ mt: 2 }} />
        </Box>
      </Container>
    );
  }

  return (
    <Container
      maxWidth="md"
      sx={{
        height: 'calc(100vh - 120px)',
        display: 'flex',
        flexDirection: 'column',
        scrollbarWidth: 'none',
        msOverflowStyle: 'none',
        '&::-webkit-scrollbar': {
          display: 'none',
        },
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
        <IconButton onClick={() => navigate('/conversations')} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {conversation?.title}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {messages.length} 条消息
          </Typography>
        </Box>
        <IconButton onClick={handleMenuOpen}>
          <MoreVert />
        </IconButton>

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
          <MenuItem onClick={() => { handleCloseMenu(); navigate(`/conversations/${conversationId}/edit`); }}>
            <Edit sx={{ mr: 1 }} /> 编辑标题
          </MenuItem>
          <MenuItem onClick={handleOrganize}>
            <Description sx={{ mr: 1 }} /> 整理为文档
          </MenuItem>
          <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
            <Delete sx={{ mr: 1 }} /> 删除对话
          </MenuItem>
        </Menu>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Messages */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          mb: 2,
          scrollbarWidth: 'none', // Firefox
          msOverflowStyle: 'none', // IE/Edge
          '&::-webkit-scrollbar': {
            display: 'none', // Chrome/Safari
          },
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 12 }}>
            <Typography variant="h6" color="text.secondary">
              开始对话
            </Typography>
            <Typography variant="body2" color="text.disabled" sx={{ mt: 1 }}>
              发送第一条消息与 AI 对话
            </Typography>
          </Box>
        ) : (
          messages.map((message, index) => (
            <Box
              key={message.message_id || index}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                mb: 3,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  maxWidth: '70%',
                  gap: 1,
                }}
              >
                {message.role === 'assistant' && (
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: 'primary.main',
                      fontSize: '0.875rem',
                    }}
                  >
                    AI
                  </Avatar>
                )}
                <Paper
                  sx={{
                    p: 2,
                    bgcolor: message.role === 'user' ? 'primary.main' : 'background.paper',
                    color: message.role === 'user' ? 'white' : 'text.primary',
                    border: message.role === 'assistant' ? '1px solid #E0E0E0' : 'none',
                  }}
                >
                  {message.role === 'assistant' ? (
                    <MarkdownRenderer content={message.content} />
                  ) : (
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {message.content}
                    </Typography>
                  )}
                </Paper>
              </Box>
            </Box>
          ))
        )}
        {streamingContent && (
          <Box
            ref={streamingMessageRef}
            sx={{
              display: 'flex',
              justifyContent: 'flex-start',
              mb: 3,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                maxWidth: '70%',
                gap: 1,
              }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: 'primary.main',
                  fontSize: '0.875rem',
                }}
              >
                AI
              </Avatar>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: 'background.paper',
                  border: '1px solid #E0E0E0',
                }}
              >
                <MarkdownRenderer content={streamingContent} />
                {sending && <span component="span" sx={{ animation: 'blink 1s infinite' }}>▋</span>}
              </Paper>
            </Box>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={sending}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 0,
            },
          }}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!newMessage.trim() || sending}
          sx={{ minWidth: 120, py: 2 }}
        >
          {sending ? '发送中...' : '发送'}
          {!sending && <Send sx={{ ml: 1 }} />}
        </Button>
      </Box>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default ChatPage;
