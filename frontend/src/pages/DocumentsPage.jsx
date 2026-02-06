import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Add,
  Search,
  MoreVert,
  Edit,
  Delete,
  Label,
} from '@mui/icons-material';
import { documentsAPI } from '../services/api';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
    tags: '',
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getList();
      setDocuments(response.data.data.items);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async () => {
    try {
      const tags = formData.tags.split(',').map(tag => tag.trim()).filter(Boolean);
      await documentsAPI.create({
        ...formData,
        tags,
      });
      setOpenDialog(false);
      setFormData({ title: '', content: '', summary: '', tags: '' });
      fetchDocuments();
    } catch (error) {
      console.error('Failed to create document:', error);
    }
  };

  const handleDeleteDocument = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个文档吗？')) {
      try {
        await documentsAPI.delete(id);
        fetchDocuments();
      } catch (error) {
        console.error('Failed to delete document:', error);
      }
    }
  };

  const handleMenuOpen = (event, doc) => {
    setAnchorEl(event.currentTarget);
    setSelectedDoc(doc);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedDoc(null);
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (doc.summary && doc.summary.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">文档</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenDialog(true)}>
          新建文档
        </Button>
      </Box>

      <TextField
        fullWidth
        placeholder="搜索文档..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
        }}
        sx={{ mb: 4 }}
      />

      {filteredDocuments.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchQuery ? '没有找到匹配的文档' : '还没有文档'}
          </Typography>
          <Typography variant="body2" color="text.disabled">
            {searchQuery ? '尝试其他关键词' : '从对话中整理或手动创建文档'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={2}>
          {filteredDocuments.map((doc) => (
            <Grid item xs={12} sm={6} md={4} key={doc.document_id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                }}
              >
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, pr: 6 }}>
                      {doc.title}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, doc)}
                      sx={{ position: 'absolute', top: 12, right: 12 }}
                    >
                      <MoreVert fontSize="small" />
                    </IconButton>
                  </Box>

                  {doc.summary && (
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {doc.summary}
                    </Typography>
                  )}

                  {doc.tags && doc.tags.length > 0 && (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 'auto' }}>
                      {doc.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={tag}
                          size="small"
                          variant="outlined"
                          icon={<Label sx={{ fontSize: 14 }} />}
                          sx={{ borderRadius: 0, height: 24 }}
                        />
                      ))}
                    </Box>
                  )}

                  <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 2 }}>
                    更新于 {new Date(doc.updated_at).toLocaleDateString('zh-CN')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>新建文档</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="标题"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
            autoFocus
          />
          <TextField
            fullWidth
            label="摘要"
            value={formData.summary}
            onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
            sx={{ mb: 2 }}
            multiline
            rows={2}
          />
          <TextField
            fullWidth
            label="内容"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            sx={{ mb: 2 }}
            multiline
            rows={6}
            placeholder="支持 Markdown 格式"
          />
          <TextField
            fullWidth
            label="标签"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            helperText="多个标签用逗号分隔"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenDialog(false)}>取消</Button>
          <Button variant="contained" onClick={handleCreateDocument}>
            创建
          </Button>
        </DialogActions>
      </Dialog>

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
        <MenuItem onClick={handleCloseMenu}>
          <Edit sx={{ mr: 1 }} /> 编辑
        </MenuItem>
        <MenuItem
          onClick={(e) => {
            handleDeleteDocument(selectedDoc?.document_id, e);
            handleCloseMenu();
          }}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} /> 删除
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default DocumentsPage;
