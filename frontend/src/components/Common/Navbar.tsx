import { Flex, Image, useBreakpointValue, IconButton, Box, Text } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import { FaBars } from "react-icons/fa"
import { FiLogOut } from "react-icons/fi"
import { useQueryClient } from "@tanstack/react-query"
import { useState } from "react"

import { useColorModeValue, ColorModeButton } from "../ui/color-mode"
import UserMenu from "./UserMenu"
import SidebarItems from "./SidebarItems" // Import SidebarItems
import useAuth from "@/hooks/useAuth" // Import useAuth for logout
import type { UserPublic } from "@/client" // Import UserPublic

import { // Import Drawer components
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
  DrawerTrigger,
} from "../ui/drawer"


function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })
  const navbarBg = "#18191B"
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const { logout } = useAuth()
  const [open, setOpen] = useState(false) // State for mobile drawer

  return (
    <Flex
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={1000}
      bg={navbarBg}
      w="100%"
      p={4}
      align="center"
      justify="space-between" // Ensure space between logo/menu and user menu
      boxShadow="sm"
    >
      {/* Mobile Menu Icon and Drawer */}
      <DrawerRoot
        placement="start"
        open={open}
        onOpenChange={(e) => setOpen(e.open)}
      >
        <DrawerBackdrop />
        <DrawerTrigger asChild>
          <IconButton
            variant="ghost"
            color="inherit"
            display={{ base: "flex", md: "none" }} // Only show on mobile
            aria-label="Open Menu"
            m={0} // Remove margin to fit in navbar
          >
            <FaBars />
          </IconButton>
        </DrawerTrigger>
        <DrawerContent maxW="xs">
          <DrawerCloseTrigger />
          <DrawerBody>
            <Flex flexDir="column" justify="space-between" h="full"> {/* Use h="full" for drawer body content */}
              <Box>
                {/* SidebarItems for mobile drawer, not horizontal */}
                <SidebarItems onClose={() => setOpen(false)} />
                <Flex
                  as="button"
                  onClick={() => {
                    logout()
                  }}
                  alignItems="center"
                  gap={4}
                  px={4}
                  py={2}
                >
                  <FiLogOut />
                  <Text>Log Out</Text>
                </Flex>
              </Box>
              {currentUser?.email && (
                <Text fontSize="sm" p={2} truncate maxW="sm">
                  Logged in as: {currentUser.email}
                </Text>
              )}
            </Flex>
          </DrawerBody>
        </DrawerContent>
      </DrawerRoot>

      {/* Desktop Navbar Content */}
      <Flex display={{ base: "none", md: "flex" }} alignItems="center" gap={4}>
        <Link to="/home">
          <Image src="/assets/images/viettel-wealth-logo.png" alt="Logo" maxW="3xs" p={2} />
        </Link>
        {/* Horizontal menu items for desktop */}
        <SidebarItems isHorizontal={true} onClose={() => {}} /> {/* Pass isHorizontal prop */}
      </Flex>

      {/* User Menu and Color Mode Toggle */}
      <Flex gap={2} alignItems="center" display={display}>
        <ColorModeButton />
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar