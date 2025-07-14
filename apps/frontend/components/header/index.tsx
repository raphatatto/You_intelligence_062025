import Image from "next/image";
import { GridContainer } from "../GridContainer";


import {FiChevronDown} from 'react-icons/fi'
import Link from "next/link";
import { ItemMenu } from "./itemMenu";
import { url } from "inspector";


const menuItems = [
    {
        url: "/",
        title: "Home",
        dropdown: false
    },
    {
        url: "/dashboard",
        title: "Dashboard",
        dropdown: false
    },
    {
        url: "/mapa",
        title: "Mapas",
        dropdown: true
    },
    {
        url: "/dados",
        title: "Dados",
        dropdown: false
    }
]

export default function Header(){
return (
    <header>
        <GridContainer>
          <div>
            <Image
                src="/icone-verde.png"
                alt="logo"
                width={30}
                height={15}
            />
            <nav>
                {menuItems.map(({ url, title, dropdown }, index) => (
                    <ItemMenu
                        key={index}
                        url={url}
                        title={title}
                        hasDropDown={dropdown}
                    />
                ))}
            </nav>
          </div>
        </GridContainer>
    </header>
)
}
