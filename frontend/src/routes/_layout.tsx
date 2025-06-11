import { Flex, Box, Button } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Navbar from "@/components/Common/Navbar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  return (
    <Flex direction="column" minH="100vh" bg="#000000">
      <Navbar />
      {/* Main content area grows to fill space */}
      <Box flex="1" p={4} pt="122px">
        <Outlet />
      </Box>
      <Box as="footer" w="100%" bg="#18191B" py={4} textAlign="center">
        <span style={{ color: "#A1A1AA", fontSize: "14px" }}>
          © 2025 Viettel Wealth. All Rights Reserved.
        </span>
      </Box>
    </Flex>
  )
}

export default Layout
// import { Flex } from "@chakra-ui/react"
// import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

// import Navbar from "@/components/Common/Navbar"
// import Sidebar from "@/components/Common/Sidebar"
// import { isLoggedIn } from "@/hooks/useAuth"

// export const Route = createFileRoute("/_layout")({
//   component: Layout,
//   beforeLoad: async () => {
//     if (!isLoggedIn()) {
//       throw redirect({
//         to: "/login",
//       })
//     }
//   },
// })

// function Layout() {
//   return (
//     <Flex direction="column" h="100vh">
//       <Navbar />
//       <Flex flex="1" overflow="hidden">
//         <Sidebar />
//         <Flex flex="1" direction="column" p={4} overflowY="auto">
//           <Outlet />
//         </Flex>
//       </Flex>
//     </Flex>
//   )
// }

// export default Layout
