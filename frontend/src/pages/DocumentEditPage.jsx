import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Paper,
  IconButton,
  Toolbar,
  Divider,
  Chip,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack,
  Save,
  Delete,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';
import MDEditor from '@uiw/react-md-editor';
import MarkdownRenderer from '../components/MarkdownRenderer';

const DocumentEditPage = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const isNew = documentId === 'new';

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [summary, setSummary] = useState('');
  const [tags, setTags] = useState('');
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });

  useEffect(() => {
    if (!isNew) {
      fetchDocument();
    }
  }, [documentId]);

  const fetchDocument = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getDetail(documentId);
      const doc = response.data.data;
      setTitle(doc.title);
      setContent(doc.content || '');
      setSummary(doc.summary || '');
      setTags(doc.tags ? doc.tags.join(', ') : '');
    } catch (error) {
      console.error('Failed to fetch document:', error);
      setSnackbar({
        open: true,
        message: '加载文档失败',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!title.trim()) {
      setSnackbar({
        open: true,
        message: '请输入标题',
        severity: 'error',
      });
      return;
    }

    try {
      setSaving(true);
      const tagsArray = tags.split(',').map(tag => tag.trim()).filter(Boolean);

      if (isNew) {
        await documentsAPI.create({
          title,
          content,
          summary,
          tags: tagsArray,
        });
      } else {
        await documentsAPI.update(documentId, {
          title,
          content,
          summary,
          tags: tagsArray,
        });
      }

      setSnackbar({
        open: true,
        message: isNew ? '创建成功' : '保存成功',
        severity: 'success',
      });

      if (isNew) {
        navigate('/documents');
      }
    } catch (error) {
      console.error('Failed to save document:', error);
      setSnackbar({
        open: true,
        message: '保存失败，请重试',
        severity: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (isNew) return;

    if (window.confirm('确定要删除这个文档吗？此操作不可恢复。')) {
      try {
        await documentsAPI.delete(documentId);
        setSnackbar({
          open: true,
          message: '删除成功',
          severity: 'success',
        });
        navigate('/documents');
      } catch (error) {
        console.error('Failed to delete document:', error);
        setSnackbar({
          open: true,
          message: '删除失败',
          severity: 'error',
        });
      }
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
      {/* 顶部工具栏 */}
      <Paper
        elevation={0}
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <Toolbar variant="dense">
          <IconButton onClick={() => navigate('/documents')} sx={{ mr: 2 }}>
            <ArrowBack />
          </IconButton>

          <TextField
            size="small"
            placeholder="文档标题"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            sx={{ flex: 1, maxWidth: 400, mr: 2 }}
            variant="outlined"
          />

          <TextField
            size="small"
            placeholder="标签（用逗号分隔）"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            sx={{ flex: 1, maxWidth: 300, mr: 2 }}
            variant="outlined"
          />

          <Box sx={{ flexGrow: 1 }} />

          {!isNew && (
            <>
              <Button
                color="error"
                startIcon={<Delete />}
                onClick={handleDelete}
                sx={{ mr: 1 }}
              >
                删除
              </Button>
              <Divider orientation="vertical" flexItem sx={{ mr: 1 }} />
            </>
          )}

          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <Save />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? '保存中...' : '保存'}
          </Button>
        </Toolbar>
      </Paper>

      {/* 摘要区域 */}
      <Paper
        elevation={0}
        sx={{
          px: 3,
          py: 2,
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder="添加摘要（可选）"
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          variant="standard"
          InputProps={{
            disableUnderline: true,
          }}
        />
      </Paper>

      {/* 编辑器和预览区域 */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', borderRight: 1, borderColor: 'divider' }}>
          <Typography
            variant="caption"
            sx={{
              px: 2,
              py: 1,
              bgcolor: 'action.hover',
              fontWeight: 600,
              color: 'text.secondary',
            }}
          >
            编辑器
          </Typography>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <MDEditor
              value={content}
              onChange={setContent}
              height="100%"
              preview="edit"
              hideToolbar={false}
              textareaProps={{
                placeholder: '开始编写你的 Markdown 内容...',
              }}
              sx={{
                '--md-editor-width': '100%',
                '--md-editor-height': '100%',
              }}
            />
          </Box>
        </Box>

        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Typography
            variant="caption"
            sx={{
              px: 2,
              py: 1,
              bgcolor: 'action.hover',
              fontWeight: 600,
              color: 'text.secondary',
            }}
          >
            预览
          </Typography>
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 3,
              bgcolor: 'background.paper',
            }}
          >
            {content ? (
              <MarkdownRenderer content={content} />
            ) : (
              <Typography variant="body2" color="text.disabled" sx={{ mt: 4 }}>
                在左侧编辑器中输入内容，这里将实时显示预览...
              </Typography>
            )}
          </Box>
        </Box>
      </Box>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DocumentEditPage;
