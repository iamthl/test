import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useParams } from "@tanstack/react-router"
import { Container, Box, Heading, Flex, Text, Button, VStack, Skeleton } from "@chakra-ui/react"
import { ItemsService } from "@/client"
import { FaArrowDown, FaArrowUp, FaPlus } from "react-icons/fa"

export const Route = createFileRoute("/_layout/asset/$assetId")({
  component: AssetDetailPage,
})

function AssetDetailPage() {
  const { assetId } = useParams("/_layout/asset/$assetId")
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
      value = desc.value ?? ""
      cumulativeReturn = desc.cumulativeReturn ?? ""
      investmentDuration = desc.investmentDuration ?? ""
    } catch {}
  }

  return (
    <Container maxW="full" py={8}>
      {/* Summary Card */}
      <Box bg="#18191B" borderRadius="lg" p={6} mb={8} boxShadow="md">
        <Flex align="center" justify="space-between" mb={4}>
          <Flex align="center" gap={2}>
            <Text fontSize="2xl" fontWeight="bold" color="#fff">
              {/* Asset icon placeholder */}
              <span role="img" aria-label="asset">📈</span> {asset?.title || <Skeleton w={32} />}
            </Text>
          </Flex>
          <Flex gap={2}>
            <Button colorScheme="red" variant="solid" size="sm">Rút tiền</Button>
            <Button colorScheme="red" variant="outline" size="sm" leftIcon={<FaPlus />}>Thêm tiền</Button>
            <Button colorScheme="gray" variant="outline" size="sm">Gợi ý đầu tư</Button>
          </Flex>
        </Flex>
        <Flex gap={8}>
          <VStack align="start" spacing={1}>
            <Text color="#fff" fontSize="md">Giá trị</Text>
            <Text color="#fff" fontWeight="bold" fontSize="lg">{value ? `${value.toLocaleString()}₫` : <Skeleton w={20} />}</Text>
          </VStack>
          <VStack align="start" spacing={1}>
            <Text color="#fff" fontSize="md">Lợi nhuận tích lũy</Text>
            <Text color="#17C964" fontWeight="bold" fontSize="lg">
              {cumulativeReturn ? `${cumulativeReturn}%` : <Skeleton w={12} />}
            </Text>
          </VStack>
          <VStack align="start" spacing={1}>
            <Text color="#fff" fontSize="md">Thời gian đầu tư</Text>
            <Text color="#fff" fontWeight="bold" fontSize="lg">
              {investmentDuration || <Skeleton w={12} />}
            </Text>
          </VStack>
        </Flex>
      </Box>

      {/* Chart Card */}
      <Box bg="#18191B" borderRadius="lg" p={6} mb={8} boxShadow="md">
        <Text color="#fff" fontWeight="bold" mb={4}>Biểu đồ giá</Text>
        {/* Chart placeholder - replace with real chart */}
        <Box h="300px" bg="#23232B" borderRadius="md" display="flex" alignItems="center" justifyContent="center">
          <Text color="#fff">[Biểu đồ giá sẽ hiển thị ở đây]</Text>
        </Box>
      </Box>

      {/* Info Cards */}
      <Box bg="#18191B" borderRadius="lg" p={6} boxShadow="md">
        <Flex borderBottom="1px solid #23232B" mb={4}>
          <Text color="#fff" fontWeight="bold" px={4} py={2} borderBottom="2px solid #FF2A3C">Tổng quan</Text>
          <Text color="#fff" px={4} py={2}>Báo cáo tài chính</Text>
        </Flex>
        <Flex gap={4} flexWrap="wrap">
          <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
            <Text fontSize="sm" color="#aaa">Tên công ty</Text>
            <Text fontWeight="bold">Tổng Công ty cổ phần Đầu tư Quốc tế Viettel</Text>
          </Box>
          <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
            <Text fontSize="sm" color="#aaa">Website</Text>
            <Text fontWeight="bold" color="#FF2A3C">www.viettelglobal.com.vn</Text>
          </Box>
          <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
            <Text fontSize="sm" color="#aaa">Lĩnh vực</Text>
            <Text fontWeight="bold">Công nghệ, Dịch vụ viễn thông</Text>
          </Box>
          <Box flex="1 1 200px" bg="#23232B" borderRadius="md" p={4} color="#fff">
            <Text fontSize="sm" color="#aaa">Thời gian công bố kết quả kinh doanh</Text>
            <Text fontWeight="bold">2025-07-05</Text>
          </Box>
        </Flex>
      </Box>
    </Container>
  )
} 