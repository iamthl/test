import { Box, Container, Heading, Button } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const suggestions = [
  {
    name: "Quỹ Dragon Capital",
    profit: "11.8%",
    risk: "Trung bình",
    riskColor: "bg-[#FFB800] text-white",
    nameColor: "text-[#FFB800]",
    duration: "2 năm",
    investColor: "bg-[#FF2A3C] text-white",
    learnColor: "border border-[#FF2A3C] text-[#FF2A3C]",
  },
  {
    name: "Quỹ VNMTF",
    profit: "9.5%",
    risk: "Thấp",
    riskColor: "bg-[#6C757D] text-white",
    nameColor: "text-[#6C757D]",
    duration: "1 năm",
    investColor: "bg-[#FF2A3C] text-white",
    learnColor: "border border-[#FF2A3C] text-[#FF2A3C]",
  },
  {
    name: "Quỹ FTSE Vietnam ETF",
    profit: "14.3%",
    risk: "Cao",
    riskColor: "bg-[#FF2A3C] text-white",
    nameColor: "text-[#FF2A3C]",
    duration: "3 năm",
    investColor: "bg-[#FF2A3C] text-white",
    learnColor: "border border-[#FF2A3C] text-[#FF2A3C]",
  },
]

const mockComparisonData = [
  { name: 'Quỹ Dragon Capital', 'Lợi nhuận kỳ vọng': 11.8, 'Tài sản hiện tại': 7.5 },
  { name: 'Quỹ VNMTF', 'Lợi nhuận kỳ vọng': 9.5, 'Tài sản hiện tại': 6.0 },
  { name: 'Quỹ FTSE Vietnam ETF', 'Lợi nhuận kỳ vọng': 14.3, 'Tài sản hiện tại': 8.0 },
];

export const Route = createFileRoute("/_layout/investment-suggestion")({
  component: InvestmentSuggestion,
})

function InvestmentSuggestion() {
  return (
    <Container maxW="full">
      <Box pt={12} m={4}>
        <Box className="bg-[#18191B] rounded-2xl p-8 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <span className="text-xl font-semibold text-white">AI Gợi ý đầu tư</span>
            <button className="text-[#FF2A3C] font-medium">Xem thêm</button>
          </div>
            <table className="w-full text-left text-white">
              <thead>
                <tr className="border-b border-[#393945]">
                  <th className="py-2 font-medium">Tên sản phẩm</th>
                  <th className="py-2 font-medium">Lợi nhuận kỳ vọng</th>
                  <th className="py-2 font-medium">Mức rủi ro</th>
                  <th className="py-2 font-medium">Thời gian đầu tư đề xuất</th>
                  <th className="py-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {suggestions.map((s, idx) => (
                  <tr key={s.name} className="border-b border-[#393945]">
                    <td className={`${s.nameColor} font-semibold`}>{s.name}</td>
                    <td>{s.profit}</td>
                    <td>
                      <span className={`px-4 py-1 rounded-lg text-sm font-semibold ${s.riskColor}`}>{s.risk}</span>
                    </td>
                    <td>{s.duration}</td>
                    <td>
                      <button className="px-5 py-3 rounded-lg font-semibold text-sm shadow {s.investColor} hover:bg-[#e02432] transition-colors">Đầu tư</button>
                      <button className="px-5 py-3 rounded-lg font-semibold text-sm {s.learnColor} hover:bg-[#000000] hover:border-[#FF2A3C] hover:text-[#FF2A3C] transition-colors">Tìm hiểu</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          <div className="mt-8">
            <div className="text-white mb-2">Biểu đồ so sánh lợi nhuận kỳ vọng của các gợi ý đầu tư với tài sản hiện tại</div>
            <div className="bg-[#18191B] rounded-xl h-48 flex items-center justify-center p-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={mockComparisonData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#fff" />
                  <YAxis stroke="#fff" tickFormatter={(value) => `${value}%`} />
                  <Tooltip
                    contentStyle={{ background: '#23232B', border: 'none', color: '#fff' }}
                    formatter={(value: number) => `${value}%`}
                  />
                  <Legend />
                  <Bar dataKey="Lợi nhuận kỳ vọng" fill="#FF2A3C" />
                  <Bar dataKey="Tài sản hiện tại" fill="#17C964" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Box>
      </Box>
    </Container>
  )
}

export default InvestmentSuggestion
