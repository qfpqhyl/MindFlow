import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Menu,
  Chip,
  Box as MuiBox,
} from '@mui/material';
import {
  Add,
  MoreVert,
  CheckCircle,
  Pending,
  EventBusy,
  Edit,
  Delete,
} from '@mui/icons-material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { tasksAPI } from '../services/api';

const TasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [openDialog, setOpenDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: null,
    reminder_enabled: true,
  });

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await tasksAPI.getList(params);
      setTasks(response.data.data.items);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      await tasksAPI.create({
        ...formData,
        due_date: formData.due_date?.toISOString(),
      });
      setOpenDialog(false);
      setFormData({ title: '', description: '', due_date: null, reminder_enabled: true });
      fetchTasks();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      await tasksAPI.complete(taskId);
      fetchTasks();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('确定要删除这个任务吗？')) {
      try {
        await tasksAPI.delete(taskId);
        fetchTasks();
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const handleMenuOpen = (event, task) => {
    setAnchorEl(event.currentTarget);
    setSelectedTask(task);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setSelectedTask(null);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'overdue':
        return <EventBusy sx={{ color: 'error.main' }} />;
      default:
        return <Pending sx={{ color: 'warning.main' }} />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'overdue':
        return '已逾期';
      default:
        return '进行中';
    }
  };

  const filteredTasks = filter === 'all' ? tasks : tasks.filter(task => task.status === filter);

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">任务</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenDialog(true)}>
          新建任务
        </Button>
      </Box>

      <ToggleButtonGroup
        value={filter}
        exclusive
        onChange={(e, value) => value && setFilter(value)}
        sx={{ mb: 4 }}
      >
        <ToggleButton value="all" sx={{ borderRadius: 0 }}>
          全部 ({tasks.length})
        </ToggleButton>
        <ToggleButton value="pending" sx={{ borderRadius: 0 }}>
          进行中 ({tasks.filter(t => t.status === 'pending').length})
        </ToggleButton>
        <ToggleButton value="completed" sx={{ borderRadius: 0 }}>
          已完成 ({tasks.filter(t => t.status === 'completed').length})
        </ToggleButton>
        <ToggleButton value="overdue" sx={{ borderRadius: 0 }}>
          已逾期 ({tasks.filter(t => t.status === 'overdue').length})
        </ToggleButton>
      </ToggleButtonGroup>

      {filteredTasks.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 12 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {filter === 'all' ? '还没有任务' : '没有找到任务'}
          </Typography>
          <Typography variant="body2" color="text.disabled">
            点击"新建任务"开始管理您的待办事项
          </Typography>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {filteredTasks.map((task) => (
            <Card key={task.task_id} sx={{ border: '1px solid #E0E0E0' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  {getStatusIcon(task.status)}
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                        {task.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {task.status === 'pending' && (
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<CheckCircle />}
                            onClick={() => handleCompleteTask(task.task_id)}
                          >
                            完成
                          </Button>
                        )}
                        <IconButton size="small" onClick={(e) => handleMenuOpen(e, task)}>
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </Box>

                    {task.description && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {task.description}
                      </Typography>
                    )}

                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                      <Chip
                        label={getStatusLabel(task.status)}
                        size="small"
                        variant="outlined"
                        sx={{ borderRadius: 0 }}
                      />
                      <Chip
                        icon={<EventBusy sx={{ fontSize: 14 }} />}
                        label={new Date(task.due_date).toLocaleString('zh-CN')}
                        size="small"
                        variant="outlined"
                        sx={{ borderRadius: 0 }}
                      />
                      {task.reminder_enabled && (
                        <Chip label="邮件提醒" size="small" sx={{ borderRadius: 0 }} />
                      )}
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>新建任务</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="任务标题"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
            autoFocus
          />
          <TextField
            fullWidth
            label="任务描述"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            sx={{ mb: 2 }}
            multiline
            rows={3}
          />
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DateTimePicker
              label="截止日期"
              value={formData.due_date}
              onChange={(value) => setFormData({ ...formData, due_date: value })}
              slotProps={{
                textField: {
                  fullWidth: true,
                  sx: { mb: 2 },
                },
              }}
            />
          </LocalizationProvider>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenDialog(false)}>取消</Button>
          <Button variant="contained" onClick={handleCreateTask}>
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
          onClick={() => {
            handleDeleteTask(selectedTask?.task_id);
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

export default TasksPage;
