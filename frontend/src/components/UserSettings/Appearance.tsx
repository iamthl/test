import { Container, Heading, Stack } from "@chakra-ui/react"
import { useTheme } from "next-themes"

import { Radio, RadioGroup } from "@/components/ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Appearance
        </Heading>

        <RadioGroup
          onValueChange={(e) => setTheme(e.value as string)}
          value={theme}
          colorPalette="red"
        >
          <Stack>
            <Radio value="system" color="white">System</Radio>
            <Radio value="light" color="white">Light Mode</Radio>
            <Radio value="dark" color="white">Dark Mode</Radio>
          </Stack>
        </RadioGroup>
      </Container>
    </>
  )
}
export default Appearance
