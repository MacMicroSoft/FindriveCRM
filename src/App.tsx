import { useState } from 'react';
import { Car, FileText, Users, MessageSquare, Menu, X, Bell, Sparkles, Star, Wrench } from 'lucide-react';
import { VehicleList } from './components/VehicleList';
import { VehicleDetails } from './components/VehicleDetails';
import { AddVehicle } from './components/AddVehicle';
import { ReportCreate } from './components/ReportCreate';
import { EditExpense } from './components/EditExpense';
import { OwnerList } from './components/OwnerList';
import { AddOwner } from './components/AddOwner';
import { OwnerChat } from './components/OwnerChat';
import { InvoiceList } from './components/InvoiceList';
import { Notifications } from './components/Notifications';
import { AIAssistant } from './components/AIAssistant';
import { SavedVehicles } from './components/SavedVehicles';
import { ServiceList } from './components/ServiceList';
import { ServiceDetails } from './components/ServiceDetails';
import { 
  mockVehicles, 
  mockOwners, 
  mockExpenses, 
  mockInvoices, 
  mockChatMessages,
  mockMaintenancePlans,
  mockComments,
  mockNotifications,
  mockAIRecommendations,
  mockServices
} from './utils/mockData';
import { Vehicle, Owner, Expense, Invoice, ChatMessage, MaintenancePlan, Comment, Notification, AIRecommendation, Service } from './types';

type Page = 
  | 'vehicles' 
  | 'vehicle-details' 
  | 'add-vehicle' 
  | 'reports' 
  | 'create-report'
  | 'edit-expense'
  | 'owners' 
  | 'add-owner' 
  | 'chat'
  | 'notifications'
  | 'ai-assistant'
  | 'saved-vehicles'
  | 'services'
  | 'service-details';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('vehicles');
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const [selectedExpenseId, setSelectedExpenseId] = useState<string | null>(null);
  const [selectedServiceId, setSelectedServiceId] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // State
  const [vehicles, setVehicles] = useState<Vehicle[]>(mockVehicles);
  const [owners, setOwners] = useState<Owner[]>(mockOwners);
  const [expenses, setExpenses] = useState<Expense[]>(mockExpenses);
  const [invoices, setInvoices] = useState<Invoice[]>(mockInvoices);
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [maintenancePlans, setMaintenancePlans] = useState<MaintenancePlan[]>(mockMaintenancePlans);
  const [comments, setComments] = useState<Comment[]>(mockComments);
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [aiRecommendations, setAIRecommendations] = useState<AIRecommendation[]>(mockAIRecommendations);
  const [services, setServices] = useState<Service[]>(mockServices);

  // Handlers
  const handleSelectVehicle = (id: string) => {
    setSelectedVehicleId(id);
    setCurrentPage('vehicle-details');
    setIsMobileMenuOpen(false);
  };

  const handleAddVehicle = (data: any) => {
    const newVehicle: Vehicle = {
      id: Date.now().toString(),
      ...data,
      status: data.isActive ? 'active' : 'processing',
      ownerName: data.ownerId ? owners.find(o => o.id === data.ownerId)?.name || null : null,
      createdAt: new Date()
    };
    setVehicles([...vehicles, newVehicle]);
    
    // Update owner's active vehicles count
    if (data.ownerId && data.isActive) {
      setOwners(owners.map(o => 
        o.id === data.ownerId 
          ? { ...o, activeVehicles: o.activeVehicles + 1 }
          : o
      ));
    }
    
    setCurrentPage('vehicles');
  };

  const handleUpdateVehicleStatus = (vehicleId: string, newStatus: Vehicle['status']) => {
    setVehicles(vehicles.map(v => 
      v.id === vehicleId ? { ...v, status: newStatus } : v
    ));
  };

  const handleChangeOwner = (vehicleId: string, ownerId: string | null) => {
    const vehicle = vehicles.find(v => v.id === vehicleId);
    const oldOwnerId = vehicle?.ownerId;
    const newOwnerName = ownerId ? owners.find(o => o.id === ownerId)?.name || null : null;
    
    setVehicles(vehicles.map(v => 
      v.id === vehicleId 
        ? { ...v, ownerId, ownerName: newOwnerName }
        : v
    ));

    // Update vehicle counts for both owners
    setOwners(owners.map(o => {
      if (o.id === oldOwnerId && vehicle?.isActive) {
        return { ...o, activeVehicles: Math.max(0, o.activeVehicles - 1) };
      }
      if (o.id === ownerId && vehicle?.isActive) {
        return { ...o, activeVehicles: o.activeVehicles + 1 };
      }
      return o;
    }));
  };

  const handleAddMaintenancePlan = (vehicleId: string, task: string, description: string, date: Date) => {
    const newPlan: MaintenancePlan = {
      id: Date.now().toString(),
      vehicleId,
      task,
      description,
      recommendedDate: date,
      completed: false,
      createdAt: new Date()
    };
    setMaintenancePlans([...maintenancePlans, newPlan]);
  };

  const handleToggleMaintenancePlan = (planId: string) => {
    setMaintenancePlans(maintenancePlans.map(p =>
      p.id === planId ? { ...p, completed: !p.completed } : p
    ));
  };

  const handleDeleteMaintenancePlan = (planId: string) => {
    setMaintenancePlans(maintenancePlans.filter(p => p.id !== planId));
  };

  const handleAddComment = (vehicleId: string, text: string) => {
    const newComment: Comment = {
      id: Date.now().toString(),
      vehicleId,
      authorId: 'manager-1',
      authorName: 'Флот-менеджер',
      text,
      createdAt: new Date()
    };
    setComments([...comments, newComment]);
  };

  const handleAddOwner = (data: any) => {
    const newOwner: Owner = {
      id: Date.now().toString(),
      ...data,
      activeVehicles: 0,
      createdAt: new Date()
    };
    setOwners([...owners, newOwner]);
    setCurrentPage('owners');
  };

  const handleCreateExpense = (data: any) => {
    const newExpense: Expense = {
      id: Date.now().toString(),
      ...data,
      currency: 'PLN' as const
    };
    setExpenses([...expenses, newExpense]);
    setCurrentPage('reports');
  };

  const handleUpdateExpense = (id: string, data: Partial<Expense>) => {
    setExpenses(expenses.map(e => 
      e.id === id ? { ...e, ...data } : e
    ));
    setCurrentPage('reports');
  };

  const handleDeleteExpense = (id: string) => {
    setExpenses(expenses.filter(e => e.id !== id));
    // Also delete associated invoice
    setInvoices(invoices.filter(i => i.expenseId !== id));
  };

  const handleUploadInvoice = (expenseId: string, file: File) => {
    const newInvoice: Invoice = {
      id: Date.now().toString(),
      number: `INV-${Date.now()}`,
      expenseId,
      fileName: file.name,
      uploadedAt: new Date()
    };
    setInvoices([...invoices, newInvoice]);
  };

  const handleSendMessage = (ownerId: string, text: string) => {
    const owner = owners.find(o => o.id === ownerId);
    const ownerVehicles = vehicles.filter(v => v.ownerId === ownerId);
    const vehicle = ownerVehicles[0]; // Get first vehicle for this owner
    
    if (!owner || !vehicle) return;

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      ownerId,
      ownerName: owner.name,
      vehicleId: vehicle.id,
      vehiclePlate: vehicle.licensePlate,
      text,
      sender: 'manager',
      timestamp: new Date(),
      read: true
    };
    setMessages([...messages, newMessage]);
  };

  const handleEditExpense = (expenseId: string) => {
    setSelectedExpenseId(expenseId);
    setCurrentPage('edit-expense');
  };

  const handleToggleSaved = (vehicleId: string) => {
    setVehicles(vehicles.map(v =>
      v.id === vehicleId ? { ...v, isSaved: !v.isSaved } : v
    ));
  };

  const handleMarkNotificationAsRead = (notificationId: string) => {
    setNotifications(notifications.map(n =>
      n.id === notificationId ? { ...n, read: true } : n
    ));
  };

  const handleDeleteNotification = (notificationId: string) => {
    setNotifications(notifications.filter(n => n.id !== notificationId));
  };

  const handleDismissRecommendation = (recommendationId: string) => {
    setAIRecommendations(aiRecommendations.filter(r => r.id !== recommendationId));
  };

  const handleSelectService = (serviceId: string) => {
    setSelectedServiceId(serviceId);
    setCurrentPage('service-details');
  };

  // Navigation
  const navigateTo = (page: Page) => {
    setCurrentPage(page);
    setIsMobileMenuOpen(false);
  };

  const navItems = [
    { id: 'vehicles' as Page, icon: Car, label: 'Автопарк' },
    { id: 'reports' as Page, icon: FileText, label: 'Витрати' },
    { id: 'services' as Page, icon: Wrench, label: 'Сервіси' },
    { id: 'owners' as Page, icon: Users, label: 'Власники' },
    { id: 'chat' as Page, icon: MessageSquare, label: 'Чат' }
  ];

  const unreadCount = messages.filter(m => !m.read && m.sender === 'owner').length;

  // Selected data
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId);
  const selectedExpense = expenses.find(e => e.id === selectedExpenseId);
  const selectedService = services.find(s => s.id === selectedServiceId);

  return (
    <div className="h-screen flex flex-col md:flex-row bg-gray-50">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:flex-col w-64 bg-white border-r border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-gray-900">Fleet Management</h1>
          <p className="text-sm text-gray-600 mt-1">Система управління автопарком</p>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 overflow-auto">
          {/* Quick Access */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 px-4 mb-2">Швидкий доступ</p>
            <button
              onClick={() => navigateTo('saved-vehicles')}
              className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                currentPage === 'saved-vehicles'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Star className="w-5 h-5" />
              <span>Збережені</span>
            </button>
            <button
              onClick={() => navigateTo('ai-assistant')}
              className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                currentPage === 'ai-assistant'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Sparkles className="w-5 h-5" />
              <span>AI Асистент</span>
            </button>
            <button
              onClick={() => navigateTo('notifications')}
              className={`w-full flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                currentPage === 'notifications'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Bell className="w-5 h-5" />
              <span>Сповіщення</span>
              {notifications.filter(n => !n.read).length > 0 && (
                <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {notifications.filter(n => !n.read).length}
                </span>
              )}
            </button>
          </div>

          {/* Main Navigation */}
          <div>
            <p className="text-xs text-gray-500 px-4 mb-2">Головне меню</p>
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => navigateTo(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  currentPage === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
                {item.id === 'chat' && unreadCount > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>
            ))}
          </div>
        </nav>
      </div>

      {/* Mobile Header */}
      <div className="md:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h1 className="text-gray-900">Fleet Management</h1>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setIsMobileMenuOpen(false)}>
          <div className="bg-white w-64 h-full p-4 space-y-2" onClick={(e) => e.stopPropagation()}>
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => navigateTo(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  currentPage === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
                {item.id === 'chat' && unreadCount > 0 && (
                  <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {currentPage === 'vehicles' && (
          <VehicleList
            vehicles={vehicles}
            onSelectVehicle={handleSelectVehicle}
            onAddVehicle={() => navigateTo('add-vehicle')}
            onToggleSaved={handleToggleSaved}
          />
        )}

        {currentPage === 'vehicle-details' && selectedVehicle && (
          <VehicleDetails
            vehicle={selectedVehicle}
            maintenancePlans={maintenancePlans}
            comments={comments}
            owners={owners}
            onBack={() => navigateTo('vehicles')}
            onUpdateStatus={handleUpdateVehicleStatus}
            onChangeOwner={handleChangeOwner}
            onAddMaintenancePlan={handleAddMaintenancePlan}
            onToggleMaintenancePlan={handleToggleMaintenancePlan}
            onDeleteMaintenancePlan={handleDeleteMaintenancePlan}
            onAddComment={handleAddComment}
          />
        )}

        {currentPage === 'add-vehicle' && (
          <AddVehicle
            owners={owners}
            onBack={() => navigateTo('vehicles')}
            onAdd={handleAddVehicle}
          />
        )}

        {currentPage === 'reports' && (
          <InvoiceList
            expenses={expenses}
            invoices={invoices}
            vehicles={vehicles}
            onEditExpense={handleEditExpense}
            onUploadInvoice={handleUploadInvoice}
            onCreateExpense={() => navigateTo('create-report')}
          />
        )}

        {currentPage === 'create-report' && (
          <ReportCreate
            vehicles={vehicles}
            services={services}
            onBack={() => navigateTo('reports')}
            onCreate={handleCreateExpense}
          />
        )}

        {currentPage === 'edit-expense' && selectedExpense && (
          <EditExpense
            expense={selectedExpense}
            vehicles={vehicles}
            onBack={() => navigateTo('reports')}
            onUpdate={handleUpdateExpense}
            onDelete={handleDeleteExpense}
          />
        )}

        {currentPage === 'owners' && (
          <OwnerList
            owners={owners}
            onAddOwner={() => navigateTo('add-owner')}
          />
        )}

        {currentPage === 'add-owner' && (
          <AddOwner
            onBack={() => navigateTo('owners')}
            onAdd={handleAddOwner}
          />
        )}

        {currentPage === 'chat' && (
          <OwnerChat
            messages={messages}
            owners={owners}
            onBack={() => navigateTo('vehicles')}
            onSendMessage={handleSendMessage}
          />
        )}

        {currentPage === 'notifications' && (
          <Notifications
            notifications={notifications}
            onBack={() => navigateTo('vehicles')}
            onMarkAsRead={handleMarkNotificationAsRead}
            onDelete={handleDeleteNotification}
          />
        )}

        {currentPage === 'ai-assistant' && (
          <AIAssistant
            recommendations={aiRecommendations}
            vehicles={vehicles}
            onBack={() => navigateTo('vehicles')}
            onDismiss={handleDismissRecommendation}
          />
        )}

        {currentPage === 'saved-vehicles' && (
          <SavedVehicles
            vehicles={vehicles}
            onBack={() => navigateTo('vehicles')}
            onSelectVehicle={handleSelectVehicle}
            onToggleSaved={handleToggleSaved}
          />
        )}

        {currentPage === 'services' && (
          <ServiceList
            services={services}
            onSelectService={handleSelectService}
          />
        )}

        {currentPage === 'service-details' && selectedService && (
          <ServiceDetails
            service={selectedService}
            vehicles={vehicles}
            expenses={expenses}
            onBack={() => navigateTo('services')}
            onSelectVehicle={handleSelectVehicle}
          />
        )}
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden bg-white border-t border-gray-200 px-2 py-2 flex items-center justify-around">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => navigateTo(item.id)}
            className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors relative ${
              currentPage === item.id
                ? 'text-blue-600'
                : 'text-gray-600'
            }`}
          >
            <item.icon className="w-6 h-6" />
            <span className="text-xs">{item.label}</span>
            {item.id === 'chat' && unreadCount > 0 && (
              <span className="absolute top-1 right-2 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Floating Action Button for Mobile */}
      {(currentPage === 'vehicles' || currentPage === 'reports' || currentPage === 'owners') && (
        <button
          onClick={() => {
            if (currentPage === 'vehicles') navigateTo('add-vehicle');
            if (currentPage === 'reports') navigateTo('create-report');
            if (currentPage === 'owners') navigateTo('add-owner');
          }}
          className="md:hidden fixed bottom-20 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-30"
        >
          {currentPage === 'vehicles' && <Car className="w-6 h-6" />}
          {currentPage === 'reports' && <FileText className="w-6 h-6" />}
          {currentPage === 'owners' && <Users className="w-6 h-6" />}
        </button>
      )}
    </div>
  );
}