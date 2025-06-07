import React from 'react';
import { formatCurrency } from '../../utils/format';

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

const Home: React.FC = () => {
  // In real implementation, this would come from props or API
  const data = mockData;

  return (
    <div className="p-6 bg-white">
      {/* Total Assets Card */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-2">Tổng tài sản</h2>
        <p className="text-2xl text-blue-600">
          {formatCurrency(data.totalAssets)} VND
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Asset Allocation Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Phân bổ tài sản</h2>
          <div className="h-[300px] flex items-center justify-center">
            <div className="relative w-64 h-64">
              {data.assetAllocation.map((item, index) => {
                const startAngle = index === 0 ? 0 : 
                  data.assetAllocation
                    .slice(0, index)
                    .reduce((acc, curr) => acc + (curr.value / 100) * 360, 0);
                const endAngle = startAngle + (item.value / 100) * 360;
                
                return (
                  <div
                    key={item.name}
                    className="absolute inset-0"
                    style={{
                      clipPath: `polygon(50% 50%, ${50 + 50 * Math.cos(startAngle * Math.PI / 180)}% ${50 + 50 * Math.sin(startAngle * Math.PI / 180)}%, ${50 + 50 * Math.cos(endAngle * Math.PI / 180)}% ${50 + 50 * Math.sin(endAngle * Math.PI / 180)}%)`,
                      backgroundColor: item.color,
                    }}
                  />
                );
              })}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-sm font-medium">Tổng</div>
                  <div className="text-lg font-bold">{formatCurrency(data.totalAssets)} VND</div>
                </div>
              </div>
            </div>
            <div className="mt-4 flex justify-center gap-4">
              {data.assetAllocation.map((item) => (
                <div key={item.name} className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm">
                    {item.name} ({item.value}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Risk Level Card */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-2">Mức độ rủi ro</h2>
          <p
            className={`text-2xl ${
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

        {/* Assets Table */}
        <div className="bg-white rounded-lg shadow-md p-6 md:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Chi tiết tài sản</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Loại tài sản</th>
                  <th className="text-right py-2">Giá trị hiện tại</th>
                  <th className="text-right py-2">Lãi suất/Lợi nhuận kỳ vọng</th>
                  <th className="text-right py-2">Ngày đáo hạn</th>
                </tr>
              </thead>
              <tbody>
                {data.assets.map((asset) => (
                  <tr key={asset.id} className="border-b">
                    <td className="py-2">{asset.type}</td>
                    <td className="text-right py-2">{formatCurrency(asset.currentValue)} VND</td>
                    <td className="text-right py-2">{asset.interestRate}%</td>
                    <td className="text-right py-2">{asset.maturityDate || 'N/A'}</td>
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