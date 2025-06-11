import React, { useState, useEffect, useRef } from 'react';
import { formatCurrency } from '../../utils/format';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import { IconButton } from '@chakra-ui/react';
import { BsThreeDotsVertical } from 'react-icons/bs';
import { MenuRoot, MenuTrigger, MenuContent } from '../ui/menu';

// Types
interface Asset {
  id: string;
  type: string;
  currentValue: number;
  interestRate: number;
  maturityDate?: string;
}

interface AssetAllocation {
  name: string;
  value: number;
  color: string;
}

interface HomeProps {
  totalAssets: number;
  assets: Asset[];
  assetAllocation: AssetAllocation[];
  riskLevel: 'Low' | 'Medium' | 'High';
}

// Mock data - Replace with real data later
const mockData: HomeProps = {
  totalAssets: 1500000000, // 1.5 billion VND
  assets: [
    {
      id: '1',
      type: 'Savings',
      currentValue: 500000000,
      interestRate: 5.5,
      maturityDate: '2024-12-31',
    },
    {
      id: '2',
      type: 'Funds',
      currentValue: 700000000,
      interestRate: 8.2,
      maturityDate: '2025-06-30',
    },
    {
      id: '3',
      type: 'Stocks',
      currentValue: 300000000,
      interestRate: 12.5,
    },
  ],
  assetAllocation: [
    { name: 'Savings', value: 33.3, color: '#0088FE' },
    { name: 'Funds', value: 46.7, color: '#00C49F' },
    { name: 'Stocks', value: 20, color: '#FFBB28' },
  ],
  riskLevel: 'Medium',
};

// Mock data for total asset value over time (for line chart)
// TODO: Replace with API call for total asset value history
const mockAssetHistory = [
  { date: '2024-01', value: 1200000000 },
  { date: '2024-02', value: 1250000000 },
  { date: '2024-03', value: 1300000000 },
  { date: '2024-04', value: 1400000000 },
  { date: '2024-05', value: 1500000000 },
];

// Custom tooltip for PieChart to show value in #FF2A3C and label in white
const PieCustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#23232B', border: 'none', color: '#fff', padding: 12}}>
        <div style={{ color: '#fff', marginBottom: 4 }}>Loại tài sản: {payload[0].name}</div>
        <div style={{ color: '#FF2A3C', fontWeight: 600 }}>{payload[0].value}%</div>
      </div>
    );
  }
  return null;
};

const Home: React.FC = () => {
  // In real implementation, this would come from props or API
  // TODO: Replace mockData with API call for all asset data, allocation, and risk level
  const [assets, setAssets] = useState(() => {
    const saved = localStorage.getItem("assets");
    return saved ? JSON.parse(saved) : mockData.assets;
  });
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    type: '',
    currentValue: '',
    interestRate: '',
    maturityDate: '',
  });
  const [editIndex, setEditIndex] = useState<number | null>(null);

  // Save assets to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem("assets", JSON.stringify(assets));
  }, [assets]);

  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Replace with API call to add or update asset
    if (editIndex !== null) {
      // Edit mode
      const updatedAssets = [...assets];
      updatedAssets[editIndex] = {
        ...updatedAssets[editIndex],
        type: form.type,
        currentValue: Number(form.currentValue),
        interestRate: Number(form.interestRate),
        maturityDate: form.maturityDate,
      };
      setAssets(updatedAssets);
    } else {
      // Add mode
      setAssets([
        ...assets,
        {
          id: String(Date.now()),
          type: form.type,
          currentValue: Number(form.currentValue),
          interestRate: Number(form.interestRate),
          maturityDate: form.maturityDate,
        },
      ]);
    }
    setForm({ type: '', currentValue: '', interestRate: '', maturityDate: '' });
    setShowForm(false);
    setEditIndex(null);
  };

  const handleEdit = (index: number) => {
    const asset = assets[index];
    setForm({
      type: asset.type,
      currentValue: asset.currentValue.toString(),
      interestRate: asset.interestRate.toString(),
      maturityDate: asset.maturityDate || '',
    });
    setEditIndex(index);
    setShowForm(true);
  };

  const handleDelete = (index: number) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa tài sản này?')) {
      setAssets(assets.filter((_: any, i: number) => i !== index));
    }
  };

  const data = { ...mockData, assets };

  return (
    <div className="p-6 bg-[#000000]">
      {/* Top summary cards row: Tổng tài sản and Phân bổ tài sản */}
      <div className="flex flex-col md:flex-row gap-6 mb-6">
        {/* Tổng tài sản + Risk Level Card */}
        <div className="bg-[#18191B] rounded-lg shadow-md p-6 flex-1 min-w-0">
          {/* TODO: Insert API data for total asset value (VND) here */}
          <h2 className="text-lg font-semibold mb-2">Tổng tài sản</h2>
          <p className="text-2xl" style={{ color: '#FF2A3C' }}>
            {formatCurrency(assets.reduce((sum: number, asset: Asset) => sum + asset.currentValue, 0))} VND
          </p>
          {/* Line chart for total asset value over time */}
          <div className="mt-8">
            <h3 className="text-base font-semibold mb-2">Biến động tổng tài sản</h3>
            {/* TODO: Replace mockAssetHistory with API data for total asset value history */}
            <div className="h-[220px] flex items-center justify-center">
              <ResponsiveContainer width="100%" height={180}>
                <LineChart data={mockAssetHistory} margin={{ top: 10, right: 30, left: 50, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="date" stroke="#fff" />
                  <YAxis stroke="#fff" tickFormatter={formatCurrency} />
                  <Tooltip formatter={(value: number) => formatCurrency(value) + ' VND'} labelFormatter={label => `Tháng: ${label}`} contentStyle={{ background: '#23232B', border: 'none', color: '#fff' }} />
                  <Line type="monotone" dataKey="value" stroke="#FF2A3C" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        {/* Asset Allocation Chart */}
        <div className="bg-[#18191B] rounded-lg shadow-md p-6 flex-1 min-w-0">
          <h2 className="text-lg font-semibold mb-4">Phân bổ tài sản</h2>
          {/* Risk Level moved here */}
          <div className="mb-4">
            <h3 className="text-base font-semibold mb-1">Khẩu vị rủi ro</h3>
            <p
              className={`text-lg ${
                data.riskLevel === 'Low'
                  ? 'text-green-600'
                  : data.riskLevel === 'Medium'
                  ? 'text-orange-600'
                  : 'text-red-600'
              }`}
            >
              {data.riskLevel}
            </p>
          </div>
          <div className="h-[300px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data.assetAllocation}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {data.assetAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  content={PieCustomTooltip}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Asset Table */}
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-[#18191B] rounded-lg shadow-md p-6 md:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Chi tiết tài sản</h2>
            {!showForm && (
              <button
                className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors flex items-center gap-2"
                onClick={() => setShowForm(true)}
              >
                <FaPlus /> Thêm tài sản
              </button>
            )}
          </div>
          {/* Add Asset Form (inline modal) */}
          {showForm && (
            <form onSubmit={handleSubmit} className="mb-4 flex flex-wrap gap-4 items-end bg-[#23232B] p-4 rounded-lg">
              <div>
                <label className="block text-sm mb-1 text-white">Loại tài sản</label>
                <input
                  type="text"
                  name="type"
                  value={form.type}
                  onChange={handleChange}
                  className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-1 text-white">Giá trị hiện tại</label>
                <input
                  type="number"
                  name="currentValue"
                  value={form.currentValue}
                  onChange={handleChange}
                  className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-1 text-white">Lãi suất/Lợi nhuận kỳ vọng</label>
                <input
                  type="number"
                  name="interestRate"
                  value={form.interestRate}
                  onChange={handleChange}
                  className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm mb-1 text-white">Ngày đáo hạn</label>
                <input
                  type="date"
                  name="maturityDate"
                  value={form.maturityDate}
                  onChange={handleChange}
                  className="px-2 py-1 rounded bg-[#18191B] text-white border border-gray-600"
                />
              </div>
              <button
                type="submit"
                className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors mt-2"
              >
                {editIndex !== null ? 'Cập nhật' : 'Lưu'}
              </button>
              <button
                type="button"
                className="ml-2 px-4 py-2 rounded-lg border border-gray-600 text-white bg-transparent hover:bg-gray-700 transition-colors mt-2"
                onClick={() => { setForm({ type: '', currentValue: '', interestRate: '', maturityDate: '' }); setShowForm(false); }}
              >
                Hủy
              </button>
            </form>
          )}
          {/* TODO: Insert API data for asset table (type, value, interest, maturity) here */}
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Loại tài sản</th>
                  <th className="text-right py-2">Giá trị hiện tại</th>
                  <th className="text-right py-2">Lãi suất/Lợi nhuận kỳ vọng</th>
                  <th className="text-right py-2">Ngày đáo hạn</th>
                  <th className="text-right py-2">Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset: Asset, idx: number) => (
                  <tr key={asset.id} className="border-b">
                    <td className="py-2">{asset.type}</td>
                    <td className="text-right py-2">{formatCurrency(asset.currentValue)} VND</td>
                    <td className="text-right py-2">{asset.interestRate}%</td>
                    <td className="text-right py-2">{asset.maturityDate || 'N/A'}</td>
                    <td className="py-2">
                      <div className="flex justify-end">
                        <MenuRoot>
                          <MenuTrigger asChild>
                            <IconButton variant="ghost" color="inherit" size="sm">
                              <BsThreeDotsVertical />
                            </IconButton>
                          </MenuTrigger>
                          <MenuContent>
                            <button
                              className="flex items-center gap-2 w-full px-4 py-2 text-white hover:bg-[#18191B]"
                              onClick={() => { handleEdit(idx); }}
                            >
                              <FaEdit /> Chỉnh sửa
                            </button>
                            <button
                              className="flex items-center gap-2 w-full px-4 py-2 text-[#FF2A3C] hover:bg-[#18191B]"
                              onClick={() => { handleDelete(idx); }}
                            >
                              <FaTrash /> Xoá
                            </button>
                          </MenuContent>
                        </MenuRoot>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 