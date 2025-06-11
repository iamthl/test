import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
  IconButton,
  MenuRoot,
  MenuTrigger,
  MenuContent,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FaEdit, FaTrash } from "react-icons/fa"
import { z } from "zod"

import { ItemsService } from "@/client"
import { ItemActionsMenu as AssetActionsMenu } from "@/components/Common/AssetActionsMenu"
import AddAsset from "@/components/Asset/AddAsset"
import PendingItems from "@/components/Pending/PendingAssets"
import { ItemPublic } from "@/client/types.gen"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const itemsSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getItemsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      ItemsService.readItems({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["items", { page }],
  }
}

export const Route = createFileRoute("/_layout/asset")({
  component: Assets,
  validateSearch: (search) => itemsSearchSchema.parse(search),
})

function AssetsTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getItemsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string | number }) => ({
        ...prev,
        page,
      }),
    })

  const items = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingItems />
  }

  if (items.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any assets yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new asset to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }} style={{ background: '#18191B' }}>
        <Table.Header>
          <Table.Row style={{ background: '#18191B' }}>
            <Table.ColumnHeader w="sm" style={{ background: '#23232B', color: '#fff' }}>Tên tài sản</Table.ColumnHeader>
            <Table.ColumnHeader w="sm" style={{ background: '#23232B', color: '#fff' }}>Giá trị</Table.ColumnHeader>
            <Table.ColumnHeader w="sm" style={{ background: '#23232B', color: '#fff' }}>Lợi nhuận tích lũy</Table.ColumnHeader>
            <Table.ColumnHeader w="sm" style={{ background: '#23232B', color: '#fff' }}>Thời gian đầu tư</Table.ColumnHeader>
            <Table.ColumnHeader w="sm" style={{ background: '#23232B', color: '#fff' }}>Thao tác</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {items?.map((item: ItemPublic) => {
            let value = '';
            let cumulativeReturn = '';
            let investmentDuration = '';
            try {
              if (item.description) {
                const desc = JSON.parse(item.description);
                value = desc.value ?? '';
                cumulativeReturn = desc.cumulativeReturn ?? '';
                investmentDuration = desc.investmentDuration ?? '';
              }
            } catch {}
            return (
              <Table.Row
                key={item.id}
                opacity={isPlaceholderData ? 0.5 : 1}
                style={{ background: '#18191B', cursor: 'pointer' }}
                className="hover:bg-[#23232B] transition-colors"
                onClick={() => navigate({ to: `/asset/${item.id}` })}
              >
                <Table.Cell truncate maxW="sm">{item.title}</Table.Cell>
                <Table.Cell truncate maxW="sm">{value}</Table.Cell>
                <Table.Cell truncate maxW="sm">{cumulativeReturn}</Table.Cell>
                <Table.Cell truncate maxW="sm">{investmentDuration}</Table.Cell>
                <Table.Cell truncate maxW="sm">
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
                  </Table.Cell>
              </Table.Row>
            )
          })}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function Assets() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Tài sản
      </Heading>
      <AddAsset />
      <AssetsTable />
    </Container>
  )
}
