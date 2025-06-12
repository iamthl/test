import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate, Outlet, useMatches } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"
import { useState } from "react"

import { ItemsService } from "@/client"
import { ItemActionsMenu as AssetActionsMenu } from "@/components/Common/AssetActionsMenu"
import AddAsset from "@/components/Asset/AddAsset"
import EditAsset from "@/components/Asset/EditAsset"
import PendingItems from "@/components/Pending/PendingAssets"
import { ItemPublic } from "@/client/types.gen"
import { formatCurrency } from "@/utils/format"
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

interface AssetsTableProps {
  editingAssetId: string | null;
  setEditingAssetId: (id: string | null) => void;
  showAddForm: boolean;
  setShowAddForm: (show: boolean) => void;
  items: ItemPublic[];
  editingItem: ItemPublic | undefined;
}

function AssetsTable({
  editingAssetId,
  setEditingAssetId,
  showAddForm,
  setShowAddForm,
  items,
  editingItem,
}: AssetsTableProps) {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const handleCellClick = (e: React.MouseEvent, itemId: string) => {
    const target = e.target as HTMLElement;
    const isActionButton = target.closest('[data-action-button="true"]');

    if (isActionButton) {
      e.stopPropagation();
      return;
    }
    navigate({ to: `/asset/${itemId}` });
  };

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

  const handleEditClick = (itemId: string) => {
    setEditingAssetId(itemId);
    setShowAddForm(false);
  }

  const handleAddClick = () => {
    setShowAddForm(true);
    setEditingAssetId(null);
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }} style={{ background: '#18191B'}}>
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
            let value: number | null = null;
            let cumulativeReturn: number | null = null;
            let investmentDuration = '';
            try {
              if (item.description) {
                const desc = JSON.parse(item.description);
                value = typeof desc.value === 'number' ? desc.value : null;
                cumulativeReturn = typeof desc.cumulativeReturn === 'number' ? desc.cumulativeReturn : null;
                investmentDuration = desc.investmentDuration ?? '';
              }
            } catch {}
            return (
              <Table.Row
                key={item.id}
                opacity={isPlaceholderData ? 0.5 : 1}
                style={{ background: '#18191B', cursor: 'pointer', borderBottom: '1px solid #393945' }}
                className="hover:text-[#FF2A3C] transition-colors"
              >
                <Table.Cell truncate maxW="sm" onClick={(e) => handleCellClick(e, item.id)}>{item.title}</Table.Cell>
                <Table.Cell truncate maxW="sm" onClick={(e) => handleCellClick(e, item.id)}>{value !== null ? `${formatCurrency(value)} VND` : ''}</Table.Cell>
                <Table.Cell truncate maxW="sm" onClick={(e) => handleCellClick(e, item.id)}>{cumulativeReturn !== null ? `${cumulativeReturn}%` : ''}</Table.Cell>
                <Table.Cell truncate maxW="sm" onClick={(e) => handleCellClick(e, item.id)}>{investmentDuration}</Table.Cell>
                <Table.Cell truncate maxW="sm">
                  <AssetActionsMenu item={item} onEditClick={() => handleEditClick(item.id)} />
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
  const matches = useMatches();
  const isAssetDetailPageActive = matches.some(match => match.routeId === '/_layout/asset/$assetId');
  const [editingAssetId, setEditingAssetId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const { page } = Route.useSearch();
  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getItemsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  });
  const items = data?.data.slice(0, PER_PAGE) ?? [];
  const editingItem = items.find(item => item.id === editingAssetId);

  const handleEditClick = (itemId: string) => {
    setEditingAssetId(itemId);
    setShowAddForm(false);
  }

  const handleAddClick = () => {
    setShowAddForm(true);
    setEditingAssetId(null);
  }

  return (
    <Container maxW="full">
      {!isAssetDetailPageActive && (
        <>
          {!editingAssetId && (
            <AddAsset showForm={showAddForm} setShowForm={setShowAddForm} />
          )}
          {editingAssetId && editingItem && (
            <div className="mb-4">
              <EditAsset
                item={editingItem}
                onCancel={() => setEditingAssetId(null)}
                onSave={() => setEditingAssetId(null)}
              />
            </div>
          )}
          <AssetsTable
            editingAssetId={editingAssetId}
            setEditingAssetId={setEditingAssetId}
            showAddForm={showAddForm}
            setShowAddForm={setShowAddForm}
            items={items}
            editingItem={editingItem}
          />
        </>
      )}
      <Outlet />
    </Container>
  )
}
