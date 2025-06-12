import { RadioGroup as ChakraRadioGroup } from "@chakra-ui/react"
import * as React from "react"

export interface RadioProps extends ChakraRadioGroup.ItemProps {
  rootRef?: React.Ref<HTMLDivElement>
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>
}

export const Radio = React.forwardRef<HTMLInputElement, RadioProps>(
  function Radio(props, ref) {
    const { children, inputProps, rootRef, ...rest } = props
    return (
      <ChakraRadioGroup.Item ref={rootRef} {...rest}>
        <ChakraRadioGroup.ItemHiddenInput ref={ref} {...inputProps} />
        <ChakraRadioGroup.ItemIndicator
          _checked={{
            borderColor: "#FF2A3C",
            background: "#FF2A3C",
            _hover: { borderColor: "#FF2A3C" },
            _active: { borderColor: "#FF2A3C" },
          }}
        />
        {children && (
          <ChakraRadioGroup.ItemText>{children}</ChakraRadioGroup.ItemText>
        )}
      </ChakraRadioGroup.Item>
    )
  },
)

export const RadioGroup = ChakraRadioGroup.Root
