import { Vehicle, Owner, Expense, Invoice, ChatMessage, MaintenancePlan, Comment, Notification, AIRecommendation, Service } from '../types';

export const mockOwners: Owner[] = [
  {
    id: '1',
    name: 'Іван Петренко',
    email: 'ivan@example.com',
    phone: '+380501234567',
    telegramUsername: '@ivan_petrenko',
    activeVehicles: 2,
    createdAt: new Date('2024-01-15')
  },
  {
    id: '2',
    name: 'Марія Коваленко',
    email: 'maria@example.com',
    phone: '+380502345678',
    telegramUsername: '@maria_kovalenko',
    activeVehicles: 1,
    createdAt: new Date('2024-02-20')
  },
  {
    id: '3',
    name: 'Олександр Шевченко',
    email: 'alex@example.com',
    phone: '+380503456789',
    activeVehicles: 0,
    createdAt: new Date('2024-03-10')
  }
];

export const mockVehicles: Vehicle[] = [
  {
    id: '1',
    vin: 'WBA3A5C50CF256833',
    licensePlate: 'AA 1234 BB',
    brand: 'BMW',
    model: '320d',
    year: 2020,
    status: 'active',
    ownerId: '1',
    ownerName: 'Іван Петренко',
    createdAt: new Date('2024-01-20'),
    isActive: true,
    isSaved: true
  },
  {
    id: '2',
    vin: 'WVWZZZ1KZBW123456',
    licensePlate: 'BB 5678 CC',
    brand: 'Volkswagen',
    model: 'Passat',
    year: 2021,
    status: 'active',
    ownerId: '2',
    ownerName: 'Марія Коваленко',
    createdAt: new Date('2024-02-25'),
    isActive: true,
    isSaved: false
  },
  {
    id: '3',
    vin: 'WAUZZZ4G7DN123456',
    licensePlate: 'CC 9012 DD',
    brand: 'Audi',
    model: 'A4',
    year: 2019,
    status: 'processing',
    ownerId: null,
    ownerName: null,
    createdAt: new Date('2024-12-01'),
    isActive: false,
    isSaved: false
  },
  {
    id: '4',
    vin: 'WDD2050091F123456',
    licensePlate: 'DD 3456 EE',
    brand: 'Mercedes-Benz',
    model: 'C-Class',
    year: 2022,
    status: 'pending-approval',
    ownerId: null,
    ownerName: null,
    createdAt: new Date('2024-12-05'),
    isActive: false,
    isSaved: false
  },
  {
    id: '5',
    vin: 'WBADT43452G123456',
    licensePlate: 'EE 7890 FF',
    brand: 'BMW',
    model: 'X5',
    year: 2021,
    status: 'maintenance',
    ownerId: '1',
    ownerName: 'Іван Петренко',
    createdAt: new Date('2024-11-15'),
    isActive: false,
    isSaved: true
  }
];

export const mockMaintenancePlans: MaintenancePlan[] = [
  {
    id: '1',
    vehicleId: '1',
    task: 'Заміна масла',
    description: 'Планова заміна моторного масла та фільтра',
    recommendedDate: new Date('2025-01-15'),
    completed: false,
    createdAt: new Date('2024-12-01')
  },
  {
    id: '2',
    vehicleId: '1',
    task: 'Перевірка гальм',
    description: 'Огляд гальмівної системи та колодок',
    recommendedDate: new Date('2025-02-01'),
    completed: false,
    createdAt: new Date('2024-12-01')
  },
  {
    id: '3',
    vehicleId: '5',
    task: 'Ремонт підвіски',
    description: 'Заміна передніх амортизаторів',
    recommendedDate: new Date('2024-12-20'),
    completed: false,
    createdAt: new Date('2024-11-20')
  },
  {
    id: '4',
    vehicleId: '2',
    task: 'Заміна шин',
    description: 'Встановлення зимових шин',
    recommendedDate: new Date('2024-12-15'),
    completed: true,
    createdAt: new Date('2024-11-10')
  }
];

export const mockExpenses: Expense[] = [
  {
    id: '1',
    vehicleId: '1',
    expenseType: 'other',
    category: 'Others',
    subcategory: 'fuel',
    description: 'Заправка дизель',
    priceType: 'quantity',
    unitPrice: 6.50,
    quantity: 50,
    currency: 'PLN',
    date: new Date('2024-12-05'),
    invoiceId: '1'
  },
  {
    id: '2',
    vehicleId: '2',
    expenseType: 'service',
    serviceId: '1',
    serviceName: 'Auto Service Pro',
    category: 'Service',
    description: 'Гальмівні колодки',
    priceType: 'total',
    totalAmount: 450,
    currency: 'PLN',
    date: new Date('2024-12-03'),
    invoiceId: '2'
  },
  {
    id: '3',
    vehicleId: '5',
    expenseType: 'service',
    serviceId: '2',
    serviceName: 'Механік Експрес',
    category: 'Service',
    description: 'Амортизатори передні',
    priceType: 'quantity',
    unitPrice: 380,
    quantity: 2,
    currency: 'PLN',
    date: new Date('2024-11-25')
  }
];

export const mockInvoices: Invoice[] = [
  {
    id: '1',
    number: 'INV-2024-001',
    expenseId: '1',
    fileName: 'fuel_receipt_dec05.pdf',
    uploadedAt: new Date('2024-12-05')
  },
  {
    id: '2',
    number: 'INV-2024-002',
    expenseId: '2',
    fileName: 'brake_pads_invoice.pdf',
    uploadedAt: new Date('2024-12-03')
  }
];

export const mockChatMessages: ChatMessage[] = [
  {
    id: '1',
    ownerId: '1',
    ownerName: 'Іван Петренко',
    vehicleId: '1',
    vehiclePlate: 'AA 1234 BB',
    text: 'Доброго дня! Коли планується наступне ТО для BMW?',
    sender: 'owner',
    timestamp: new Date('2024-12-10T10:30:00'),
    read: true
  },
  {
    id: '2',
    ownerId: '1',
    ownerName: 'Іван Петренко',
    vehicleId: '1',
    vehiclePlate: 'AA 1234 BB',
    text: 'Вітаю! Планова заміна масла рекомендується 15 січня 2025',
    sender: 'manager',
    timestamp: new Date('2024-12-10T10:45:00'),
    read: true
  },
  {
    id: '3',
    ownerId: '2',
    ownerName: 'Марія Коваленко',
    vehicleId: '2',
    vehiclePlate: 'BB 5678 CC',
    text: 'Добрий день! Чи можна подивитись звіт по витратам за місяць?',
    sender: 'owner',
    timestamp: new Date('2024-12-11T14:20:00'),
    read: false
  }
];

export const mockComments: Comment[] = [
  {
    id: '1',
    vehicleId: '3',
    authorId: 'manager-1',
    authorName: 'Флот-менеджер',
    text: 'Авто потребує детального огляду перед узгодженням',
    createdAt: new Date('2024-12-02')
  },
  {
    id: '2',
    vehicleId: '5',
    authorId: 'manager-1',
    authorName: 'Флот-менеджер',
    text: 'Замовлено запчастини для ремонту підвіски',
    createdAt: new Date('2024-11-22')
  }
];

export const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'maintenance_reminder',
    title: 'Нагадування про ТО',
    message: 'Надіслано повідомлення Власнику Іван Петренко з Авто BMW 320d (AA 1234 BB) про заміну масла',
    vehicleId: '1',
    ownerId: '1',
    timestamp: new Date('2024-12-10T10:45:00'),
    read: false
  },
  {
    id: '2',
    type: 'expense_added',
    title: 'Додано витрату',
    message: 'Додано витрату на паливо для Volkswagen Passat (BB 5678 CC) - 325.00 PLN',
    vehicleId: '2',
    timestamp: new Date('2024-12-05T15:30:00'),
    read: false
  },
  {
    id: '3',
    type: 'status_change',
    title: 'Зміна статусу',
    message: 'Авто Mercedes-Benz C-Class (DD 3456 EE) переведено на узгодження',
    vehicleId: '4',
    timestamp: new Date('2024-12-05T12:00:00'),
    read: true
  }
];

export const mockAIRecommendations: AIRecommendation[] = [
  {
    id: '1',
    vehicleId: '1',
    type: 'maintenance',
    title: 'Рекомендується заміна масла',
    description: 'BMW 320d (AA 1234 BB) потребує планової заміни масла. Рекомендована дата: 15 січня 2025',
    priority: 'high',
    createdAt: new Date('2024-12-01')
  },
  {
    id: '2',
    vehicleId: '2',
    type: 'maintenance',
    title: 'Перевірка гальмівної системи',
    description: 'Volkswagen Passat остання перевірка гальм була 6 місяців тому',
    priority: 'medium',
    createdAt: new Date('2024-12-01')
  },
  {
    id: '3',
    vehicleId: '5',
    type: 'cost_alert',
    title: 'Підвищені витрати на ремонт',
    description: 'BMW X5 витрати на ремонт підвіски перевищують середні на 25%',
    priority: 'medium',
    createdAt: new Date('2024-11-25')
  }
];

export const mockServices: Service[] = [
  {
    id: '1',
    name: 'Auto Service Pro',
    address: 'вул. Сервісна 15, Варшава',
    phone: '+48 123 456 789',
    email: 'info@autoservicepro.pl',
    activeVehicles: 2,
    createdAt: new Date('2024-01-10')
  },
  {
    id: '2',
    name: 'Механік Експрес',
    address: 'вул. Ремонтна 8, Краків',
    phone: '+48 234 567 890',
    email: 'contact@mechanicexpress.pl',
    activeVehicles: 1,
    createdAt: new Date('2024-02-15')
  },
  {
    id: '3',
    name: 'CarFix Center',
    address: 'вул. Автомобільна 22, Вроцлав',
    phone: '+48 345 678 901',
    activeVehicles: 0,
    createdAt: new Date('2024-03-20')
  }
];