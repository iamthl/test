import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useParams, useNavigate } from "@tanstack/react-router"
import { Container, Box, Heading, Flex, Text, Button, VStack, Skeleton, Table } from "@chakra-ui/react"
import { Tabs, TabList, Tab, TabPanels, TabPanel } from "@chakra-ui/tabs"
import { ItemsService } from "@/client"
import { FaArrowDown, FaArrowUp, FaPlus, FaPiggyBank, FaChartLine, FaBuilding, FaGlobe, FaCalendarAlt, FaArrowLeft, FaUpload } from "react-icons/fa"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const Route = createFileRoute("/_layout/asset/$assetId")({
  component: AssetDetailPage,
})

// Mock data for the price chart
const mockPriceData = [
  { name: 'Tháng 6', price: 100000, trend: 'up' },
  { name: 'Tháng 7', price: 110000, trend: 'up' },
  { name: 'Tháng 8', price: 90000, trend: 'down' },
  { name: 'Tháng 10', price: 80000, trend: 'down' },
  { name: 'Tháng 12', price: 89600, trend: 'up' },
  { name: '2025-01', price: 95000, trend: 'up' },
  { name: 'Tháng 3', price: 70000, trend: 'down' },
  { name: 'Tháng 5', price: 67039, trend: 'down' },
];

// Mock data for the financial report table
const mockFinancialReportData = [
  { year: '2023', revenue: 1500000000, profit: 500000000, ebitda: 700000000 },
  { year: '2022', revenue: 1200000000, profit: 400000000, ebitda: 600000000 },
  { year: '2021', revenue: 1000000000, profit: 300000000, ebitda: 500000000 },
];

function AssetDetailPage() {
  const { assetId } = Route.useParams()
  const navigate = useNavigate()
  const { data: asset, isLoading } = useQuery({
    queryKey: ["asset", assetId],
    queryFn: () => ItemsService.readItem({ id: assetId }),
  })

  let value = ""
  let cumulativeReturn = ""
  let investmentDuration = ""
  if (asset?.description) {
    try {
      const desc = JSON.parse(asset.description)
      value = desc.value ? desc.value.toLocaleString() : ""
      cumulativeReturn = desc.cumulativeReturn ?? ""
      investmentDuration = desc.investmentDuration ?? ""
    } catch {}
  }

  const formatCurrency = (num: number) => {
    return num.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
  };

  // Custom Tooltip for Price Chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const price = payload[0].value;
      const trend = payload[0].payload.trend;
      const color = trend === 'up' ? '#17C964' : '#FF2A3C';

      return (
        <div style={{ background: '#23232B', border: 'none', color: '#fff', padding: 12 }}>
          <p className="font-bold">{`Tháng: ${label}`}</p>
          <p style={{ color: color }}>{`Giá: ${formatCurrency(price)}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Container maxW="full" py={8}>
      <Button
        onClick={() => navigate({ to: "/asset" })}
        colorScheme="red"
        variant="solid"
        mb={4}
      >
        <FaArrowLeft style={{ color: 'white', marginRight: '8px' }} />
        Quay lại 
      </Button>

      {/* Summary Card */}
      <Box bg="#18191B" borderRadius="lg" p={6} mb={8} boxShadow="md">
        <Flex align="center" justify="space-between" mb={4}>
          <Flex align="center" gap={2}>
            <Text fontSize="2xl" fontWeight="bold" color="#FF2A3C">
              <FaPiggyBank style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }} />
              {asset?.title || <Skeleton w={32} />}
            </Text>
          </Flex>
          <Flex gap={2}>
            <Button className="bg-[#FF2A3C] text-white font-semibold px-4 py-2 rounded-lg shadow hover:bg-[#e02432] transition-colors flex items-center gap-2"
            >
              <FaPlus style={{ marginRight: '3px' }} />
              Thêm tài sản
            </Button>
            <Button className=" borderColor-[#FF2A3C] border-2 text-white font-semibold px-4 py-2 rounded-lg shadow transition-colors flex items-center gap-2"
            >
              <FaUpload style={{ marginRight: '3px' }} />
              Rút tiền
            </Button>

          </Flex>
        </Flex>
        <Flex gap={8}>
          <Flex direction="column" align="start" gap="1">
            <Text color="#fff" fontSize="md">Giá trị</Text>
            <Text color="#fff" fontWeight="bold" fontSize="lg">{value ? `${value} VND` : <Skeleton w={20} />}</Text>
          </Flex>
          <Flex direction="column" align="start" gap="1">
            <Text color="#fff" fontSize="md">Lợi nhuận tích lũy</Text>
            <Text color="#17C964" fontWeight="bold" fontSize="lg">
              {cumulativeReturn ? `${cumulativeReturn}%` : <Skeleton w={12} />}
            </Text>
          </Flex>
          <Flex direction="column" align="start" gap="1">
            <Text color="#fff" fontSize="md">Thời gian đầu tư</Text>
            <Text color="#fff" fontWeight="bold" fontSize="lg">
              {investmentDuration || <Skeleton w={12} />}
            </Text>
          </Flex>
        </Flex>
      </Box>

      {/* Chart Card */}
      <Box bg="#18191B" borderRadius="lg" p={6} mb={8} boxShadow="md">
        <Flex justify="space-between" align="center" mb={4}>
          <Text color="#fff" fontWeight="bold">Biểu đồ giá</Text>
          <Flex gap={2}>
            <Button size="xs" variant="outline" colorScheme="gray" onClick={() => console.log('1m')}>1m</Button>
            <Button size="xs" variant="outline" colorScheme="gray" onClick={() => console.log('3m')}>3m</Button>
            <Button size="xs" variant="outline" colorScheme="gray" onClick={() => console.log('1y')}>1y</Button>
          </Flex>
        </Flex>
        <Box h="300px" bg="#18191B" borderRadius="md" p={4}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={mockPriceData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#FF2A3C" // Default red for line
                strokeWidth={2}
                dot={false}
              />
              {/* Separate lines for conditional coloring (green/red) */}
              <Line
                type="monotone"
                dataKey="price"
                stroke="#17C964" // Green for positive trend
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#FF2A3C" // Red for negative trend
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </Box>

      {/* Info Cards and Financial Report Tabs */}
      <Box bg="#18191B" borderRadius="lg" p={6} boxShadow="md">
        <Tabs variant="unstyled">
          <TabList borderBottom="1px solid #23232B" mb={25}>
            <Tab _selected={{ color: '#FF2A3C', fontWeight: 'bold', borderBottom: '2px solid #FF2A3C' }} color="#fff" px={4} py={2} mr="25px">Tổng quan</Tab>
            <Tab _selected={{ color: '#FF2A3C', fontWeight: 'bold', borderBottom: '2px solid #FF2A3C' }} color="#fff" px={4} py={2}>Báo cáo tài chính</Tab>
          </TabList>
          <TabPanels>
            <TabPanel p={0}>
              <Flex gap={4} flexWrap="wrap">
                <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
                  <Text fontSize="sm" color="#aaa"><FaBuilding style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }} />Tên công ty</Text>
                  <Text fontWeight="bold">Tổng Công ty cổ phần Đầu tư Quốc tế Viettel</Text>
                </Box>
                <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
                  <Text fontSize="sm" color="#aaa"><FaGlobe style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }} />Website</Text>
                  <Text fontWeight="bold" color="#FF2A3C">www.viettelglobal.com.vn</Text>
                </Box>
                <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
                  <Text fontSize="sm" color="#aaa"><FaChartLine style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }} />Lĩnh vực</Text>
                  <Text fontWeight="bold">Công nghệ, Dịch vụ viễn thông</Text>
                </Box>
                <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
                  <Text fontSize="sm" color="#aaa"><FaCalendarAlt style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }} />Thời gian công bố kết quả kinh doanh</Text>
                  <Text fontWeight="bold">2025-07-05</Text>
                </Box>
              </Flex>
            </TabPanel>
            <TabPanel p={0}>
              <Table.Root size={{ base: "sm", md: "md" }} style={{ background: '#23232B' }}>
                <Table.Header>
                  <Table.Row style={{ background: '#23232B' }}>
                    <Table.ColumnHeader style={{ background: '#23232B', color: '#fff' }}>Năm</Table.ColumnHeader>
                    <Table.ColumnHeader style={{ background: '#23232B', color: '#fff' }}>Doanh thu</Table.ColumnHeader>
                    <Table.ColumnHeader style={{ background: '#23232B', color: '#fff' }}>Lợi nhuận</Table.ColumnHeader>
                    <Table.ColumnHeader style={{ background: '#23232B', color: '#fff' }}>EBITDA</Table.ColumnHeader>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {mockFinancialReportData.map((report, index) => (
                    <Table.Row key={index} style={{ background: '#18191B' }}>
                      <Table.Cell color="#fff">{report.year}</Table.Cell>
                      <Table.Cell color="#fff">{formatCurrency(report.revenue)}</Table.Cell>
                      <Table.Cell color="#17C964">{formatCurrency(report.profit)}</Table.Cell>
                      <Table.Cell color="#fff">{formatCurrency(report.ebitda)}</Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Container>
  )
} 