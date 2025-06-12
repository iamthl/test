import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"
import { FaEdit } from "react-icons/fa"

import type { ItemPublic } from "@/client"
import DeleteAsset from "../Asset/DeleteAsset"

interface ItemActionsMenuProps {
  item: ItemPublic;
  onEditClick: () => void;
}

export const ItemActionsMenu = ({ item, onEditClick }: ItemActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit" onClick={(e) => e.stopPropagation()}>
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <button
          className="flex items-center gap-2 w-full px-4 py-2 text-white hover:bg-[#18191B]"
          onClick={() => {
            onEditClick();
          }}
        >
          <FaEdit /> Chỉnh sửa
        </button>
        <DeleteAsset id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
