import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiBriefcase, FiHome, FiUsers } from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import type { UserPublic } from "@/client"

const items = [
  { icon: FiHome, title: "Tổng quan", path: "/home" },
  { icon: FiBriefcase, title: "Tài sản", path: "/asset" },
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

const SidebarItems = ({ onClose, isHorizontal }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems: Item[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items

  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose}
      // Apply horizontal specific styles if needed, or rely on parent Flex
      style={isHorizontal ? { textDecoration: 'none' } : {}}
    >
      <Flex
        gap={isHorizontal ? 2 : 4} // Smaller gap for horizontal menu
        px={isHorizontal ? 2 : 4} // Smaller padding for horizontal menu
        py={isHorizontal ? 1 : 2} // Smaller padding for horizontal menu
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
        flexDirection="row" // Items remain in a row within their link
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={isHorizontal ? 1 : 2}>{title}</Text> {/* Smaller margin for horizontal */}
      </Flex>
    </RouterLink>
  ))

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