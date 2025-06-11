import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink, useRouterState } from "@tanstack/react-router"
import { FiBriefcase, FiHome, FiUsers, FiTrendingUp } from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import type { UserPublic } from "@/client"

const items = [
  { icon: FiHome, title: "Tổng quan", path: "/home" },
  { icon: FiBriefcase, title: "Tài sản", path: "/asset" },
  { icon: FiTrendingUp, title: "Đề xuất đầu tư", path: "/investment-suggestion" },
]

interface SidebarItemsProps {
  onClose?: () => void;
  isHorizontal?: boolean; // New prop to control layout
}

interface Item {
  icon: IconType
  title: string
  path: string
}

function normalizePath(p: string) {
  return p.replace(/\/+$/, '');
}

const SidebarItems = ({ onClose, isHorizontal }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems: Item[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items

  const { location } = useRouterState();
  const normalizedCurrentPath = normalizePath(location.pathname);

  const listItems = finalItems.map(({ icon, title, path }) => {
    const normalizedPath = normalizePath(path);
    const isActive =
      normalizedCurrentPath === normalizedPath ||
      (normalizedPath !== '' && normalizedPath !== '/' && normalizedCurrentPath.startsWith(normalizedPath + '/'));
    return (
      <RouterLink key={title} to={path} onClick={onClose}
        style={isHorizontal ? { textDecoration: 'none' } : {}}
      >
        <Flex
          gap={isHorizontal ? 2 : 4}
          px={isHorizontal ? 2 : 4}
          py={isHorizontal ? 1 : 2}
          _hover={{
            background: "gray.subtle",
          }}
          alignItems="center"
          fontSize="sm"
          flexDirection="row"
          style={isActive ? { color: '#FF2A3C', fontWeight: 'bold' } : {}}
        >
          <Icon as={icon} alignSelf="center" />
          <Text ml={isHorizontal ? 1 : 2}>{title}</Text>
        </Flex>
      </RouterLink>
    );
  });

  // Render horizontally for Navbar, or vertically for mobile drawer/old sidebar
  if (isHorizontal) {
    return (
      <Flex alignItems="center" gap={0}> {/* Gap controlled by internal item padding */}
        {listItems}
      </Flex>
    )
  }

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        Menu
      </Text>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems
