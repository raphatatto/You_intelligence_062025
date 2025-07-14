import Link from "next/link";
import { FiChevronDown } from "react-icons/fi";

interface ItemMenuProps{
    url: string
    title: string
    hasDropDown?: boolean
}

export function ItemMenu({url, title, hasDropDown} : ItemMenuProps){
    return (
        <Link href={url} className="flex items-center gap-8 font-semibold hover:opacity-80 transition-opacity">{title} {hasDropDown && <FiChevronDown/>}</Link>
    )
}