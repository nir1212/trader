import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  ShowChart,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getPortfolioSummary, getPortfolioSnapshots } from '../services/api';
import type { PortfolioSummary, Snapshot } from '../types';

export default function Dashboard() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const portfolioData = await getPortfolioSummary(1);
      setSummary(portfolioData);
      
      const snapshotData = await getPortfolioSnapshots(1, 30);
      setSnapshots(Array.isArray(snapshotData) ? snapshotData.reverse() : []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!summary) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography variant="h6" color="text.secondary">
          No portfolio data available
        </Typography>
      </Box>
    );
  }

  const isProfitable = (summary.total_pnl || 0) >= 0;

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
        Overview of your trading portfolio
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3} component="div">
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Value
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    ${(summary.total_value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </Typography>
                </Box>
                <AccountBalance color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3} component="div">
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    P&L
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color={isProfitable ? 'success.main' : 'error.main'}>
                    ${(summary.total_pnl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </Typography>
                  <Typography variant="body2" color={isProfitable ? 'success.main' : 'error.main'}>
                    {(summary.total_pnl_pct || 0).toFixed(2)}%
                  </Typography>
                </Box>
                {isProfitable ? (
                  <TrendingUp color="success" sx={{ fontSize: 40 }} />
                ) : (
                  <TrendingDown color="error" sx={{ fontSize: 40 }} />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3} component="div">
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Cash Available
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    ${(summary.cash || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </Typography>
                </Box>
                <AccountBalance color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3} component="div">
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Open Positions
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {summary.num_positions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ${(summary.positions_value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </Typography>
                </Box>
                <ShowChart color="secondary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Portfolio Value Chart */}
      {snapshots.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Portfolio Value Over Time
            </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={snapshots}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleString()}
                formatter={(value) => [`$${typeof value === 'number' ? value.toFixed(2) : '0.00'}`, 'Value']}
              />
              <Line 
                type="monotone" 
                dataKey="total_value" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Current Positions */}
      {(summary.num_positions || 0) > 0 && summary.positions && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Current Positions
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Symbol</strong></TableCell>
                    <TableCell align="right"><strong>Quantity</strong></TableCell>
                    <TableCell align="right"><strong>Entry Price</strong></TableCell>
                    <TableCell align="right"><strong>Current Price</strong></TableCell>
                    <TableCell align="right"><strong>Value</strong></TableCell>
                    <TableCell align="right"><strong>P&L</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                {Object.entries(summary.positions).map(([symbol, position]) => (
                  <TableRow key={symbol} hover>
                    <TableCell component="th" scope="row">
                      <Typography fontWeight="bold">{symbol}</Typography>
                    </TableCell>
                    <TableCell align="right">{position.quantity.toFixed(2)}</TableCell>
                    <TableCell align="right">${position.entry_price.toFixed(2)}</TableCell>
                    <TableCell align="right">${position.current_price.toFixed(2)}</TableCell>
                    <TableCell align="right">${position.value.toFixed(2)}</TableCell>
                    <TableCell align="right">
                      <Typography
                        fontWeight="bold"
                        color={position.pnl >= 0 ? 'success.main' : 'error.main'}
                      >
                        ${position.pnl.toFixed(2)} ({position.pnl_pct.toFixed(2)}%)
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
